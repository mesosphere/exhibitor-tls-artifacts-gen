import click
import os
import shutil

from .gen_certificates import CertificateGenerator
from .gen_stores import KeystoreGenerator


@click.command()
@click.argument('sa_names', nargs=-1)
@click.option('-d', '--dir', help='Directory to put artifacts in.',
              default='./artifact/')
def app(sa_names, dir):
    os.makedirs(dir)

    if len(sa_names) < 1:
        sa_names = [u'localhost']

    try:
        cert_generator = CertificateGenerator(dir)
        root = cert_generator.get_cert(cert_name=u'root')
        client = cert_generator.get_cert(cert_name=u'client', issuer=root,
                                         sa_names=sa_names)
        server = cert_generator.get_cert(cert_name=u'server', issuer=root,
                                         sa_names=sa_names)

        store_generator = KeystoreGenerator(dir)
        store_generator.create_truststore([root.cert_path])
        store_generator.create_entitystore(client.cert_path,
                                           client.key_path,
                                           client.password.decode('utf-8'),
                                           store_name=u'clientstore')
        store_generator.create_entitystore(server.cert_path,
                                           server.key_path,
                                           server.password.decode('utf-8'),
                                           store_name=u'serverstore')
    except Exception as e:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        raise e


if __name__ == '__main__':
    app()
