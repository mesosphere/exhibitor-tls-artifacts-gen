import click
import os
import shutil

from .gen_certificates import CertificateGenerator
from .gen_stores import KeystoreGenerator
from .validators import validate_dir_missing


@click.command(name='exhibitor-tls-artifacts')
@click.argument('nodes', nargs=-1)
@click.option(
    '-d',
    '--output-directory',
    help='Directory to put artifacts in. This output_directory must not exist.',
    default='./artifacts/',
    callback=validate_dir_missing)
def app(nodes, output_directory):
    """
    Generates Admin Router and Exhibitor TLS artifacts. NODES should consist
    of a space separated list of master ip addresses. See
    https://docs.mesosphere.com/1.13/security/ent/tls-ssl/exhibitor/
    """
    if not nodes:
        raise click.BadArgumentUsage('No nodes have been provided.')

    # Create artifact output_directory
    os.makedirs(output_directory)

    # Admin Router is configured to use the URI ` http://exhibitor/` to reach
    # the local Exhibitor. To make hostname verification pass `exhibitor`
    # needs to be present as a subject alternative name (of type `DNSname`).
    # Also see https://trac.nginx.org/nginx/ticket/1307

    sans = ['localhost', 'exhibitor', '127.0.0.1']

    try:
        cert_generator = CertificateGenerator(output_directory)
        root_cert_path, root_key_path = cert_generator.get_cert(
            cert_name='root')
        store_generator = KeystoreGenerator(output_directory)
        root_truststore = store_generator.create_truststore([root_cert_path])

        for node in nodes:
            node_path_name = str(node)
            client_cert_path, client_key_path = cert_generator.get_cert(
                cert_name='client',
                node_cert_path=node_path_name,
                issuer=(root_cert_path, root_key_path),
                sa_names=sans + [node])
            server_cert_path, server_key_path = cert_generator.get_cert(
                cert_name='server',
                node_cert_path=node_path_name,
                issuer=(root_cert_path, root_key_path),
                sa_names=sans + [node])

            store_generator.create_entitystore(client_cert_path,
                                               client_key_path,
                                               store_name='clientstore',
                                               node_cert_path=node_path_name)
            store_generator.create_entitystore(server_cert_path,
                                               server_key_path,
                                               store_name='serverstore',
                                               node_cert_path=node_path_name)
            os.remove(server_cert_path)
            os.remove(server_key_path)

            shutil.copy(root_cert_path, client_cert_path.parent)
            shutil.copy(root_truststore, client_cert_path.parent)
        os.remove(root_key_path)

    except Exception as e:
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
        raise e


if __name__ == '__main__':
    app()
