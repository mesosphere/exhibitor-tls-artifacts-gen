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
        sans = ['localhost']

    try:
        cert_generator = CertificateGenerator(dir)
        root = cert_generator.get_cert(cert_name='root')
        client = cert_generator.get_cert(cert_name='client', issuer=root,
                                         sa_names=sans)
        server = cert_generator.get_cert(cert_name='server', issuer=root,
                                         sa_names=sans)

        store_generator = KeystoreGenerator(dir)
        store_generator.create_truststore([root.cert_path])
        store_generator.create_entitystore(client.cert_path,
                                           client.key_path,
                                           store_name='clientstore')
        store_generator.create_entitystore(server.cert_path,
                                           server.key_path,
                                           store_name='serverstore')

        # Remove not needed files
        os.remove(server.cert_path)
        os.remove(server.key_path)
        os.remove(root.key_path)

    except Exception as e:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        raise e


if __name__ == '__main__':
    app()
