import click
import os
import shutil

from .gen_certificates import CertificateGenerator
from .gen_stores import KeystoreGenerator


@click.command()
@click.argument('sans', nargs=-1)
@click.option('-d', '--dir', help='Directory to put artifacts in.',
              default='./artifacts/')
def app(sans, dir):
    os.makedirs(dir)

    if len(sans) < 1:
        sans = ['localhost', '127.0.0.1']

    try:
        cert_generator = CertificateGenerator(dir)
        root_cert_path, root_key_path = cert_generator.get_cert(
            cert_name='root')
        client_cert_path, client_key_path = cert_generator.get_cert(
            cert_name='client', issuer=(root_cert_path, root_key_path),
            sa_names=sans)
        server_cert_path, server_key_path = cert_generator.get_cert(
            cert_name='server', issuer=(root_cert_path, root_key_path),
            sa_names=sans)

        store_generator = KeystoreGenerator(dir)
        store_generator.create_truststore([root_cert_path])
        store_generator.create_entitystore(client_cert_path,
                                           client_key_path,
                                           store_name='clientstore')
        store_generator.create_entitystore(server_cert_path,
                                           server_key_path,
                                           store_name='serverstore')

        # Remove not needed files
        os.remove(server_cert_path)
        os.remove(server_key_path)
        os.remove(root_key_path)

    except Exception as e:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        raise e


if __name__ == '__main__':
    app()
