import click
import os
import shutil
import sys
from pathlib import Path

from .gen_certificates import CertificateGenerator
from .gen_stores import KeystoreGenerator


@click.command()
@click.argument('nodes', nargs=-1)
@click.option('-d', '--dir', help='Directory to put artifacts in.',
              default='./artifacts/')
def app(nodes, dir):
    """
    Generates Admin Router and Exhibitor TLS artifacts. NODES should consist
    of a space seperated list of master ip addresses. See
    https://docs.mesosphere.com/1.13/security/ent/tls-ssl/exhibitor-tls/
    """
    dir = Path(dir)
    if dir.exists():
        print('{} already exists.'.format(dir))
        sys.exit(1)

    if not nodes:
        print('No nodes have been provided.')
        sys.exit(1)

    # Create artifact directory
    os.makedirs(dir)

    # Admin router (nginx) requires `exhibitor` to exist as a SAN on all nodes
    # due to peculiarity in the nginx TLS client.
    # https://stackoverflow.com/questions/44828550/nginx-ssl-upstream-verify-fail
    # https://trac.nginx.org/nginx/ticket/1307
    sans = ['localhost', 'exhibitor', '127.0.0.1']

    try:
        cert_generator = CertificateGenerator(dir)
        root_cert_path, root_key_path = cert_generator.get_cert(
            cert_name='root')
        store_generator = KeystoreGenerator(dir)
        root_truststore = store_generator.create_truststore([root_cert_path])

        for node in nodes:
            node_path_name = 'node_' + node.replace('.', '_')
            client_cert_path, client_key_path = cert_generator.get_cert(
                cert_name='client', node_cert_path=node_path_name, issuer=(root_cert_path, root_key_path),
                sa_names=sans + [node])
            server_cert_path, server_key_path = cert_generator.get_cert(
                cert_name='server', node_cert_path=node_path_name, issuer=(root_cert_path, root_key_path),
                sa_names=sans + [node])

            store_generator.create_entitystore(client_cert_path,
                                               client_key_path,
                                               store_name='clientstore', node_cert_path=node_path_name)
            store_generator.create_entitystore(server_cert_path,
                                               server_key_path,
                                               store_name='serverstore', node_cert_path=node_path_name)
            os.remove(server_cert_path)
            os.remove(server_key_path)

            shutil.copy(root_cert_path, client_cert_path.parent)
            shutil.copy(root_truststore, client_cert_path.parent)
        os.remove(root_key_path)

    except Exception as e:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        raise e


if __name__ == '__main__':
    app()
