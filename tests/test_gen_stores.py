import re

from exhibitor_tls_artifacts.gen_artifacts import CertificateGenerator
from exhibitor_tls_artifacts.gen_stores import KeystoreGenerator
from subprocess import Popen, PIPE
from tempfile import TemporaryDirectory


class TestGenStores:
    """
    Test that certificates are imported correctly in the `.jks` keystores.
    """

    def test_create_truststore(self):
        with TemporaryDirectory() as test_dir:
            cert_gen = CertificateGenerator(artifact_dir=test_dir)

            cert_name = 'testcert'
            cert_path, _ = cert_gen.get_cert(cert_name=cert_name)

            store_gen = KeystoreGenerator(test_dir)

            store_name = 'teststore'
            store_pass = 'testpass'
            store_gen.create_truststore(
                [cert_path],
                name=store_name,
                password=store_pass
            )

            cmd = [
                'keytool',
                '-keystore',
                test_dir + '/' + store_name + '.jks',
                '-list',
                '-storepass',
                store_pass
            ]

            proc = Popen(cmd, stderr=PIPE, stdout=PIPE)
            stdout, stderr = proc.communicate()

            assert proc.wait() == 0
            assert re.search(cert_name + '-cert', stdout.decode())
            assert re.search('trustedCertEntry', stdout.decode())

    def test_create_entitystore(self):
        with TemporaryDirectory() as test_dir:
            cert_gen = CertificateGenerator(artifact_dir=test_dir)

            cert_name = 'test'
            cert_path, key_path = cert_gen.get_cert(cert_name=cert_name)

            store_gen = KeystoreGenerator(test_dir)

            store_name = 'teststore'
            store_pass = 'testpass'

            store_gen.create_entitystore(
                cert_path,
                key_path,
                store_name=store_name,
                store_password=store_pass
            )

            cmd = [
                'keytool',
                '-keystore',
                test_dir + '/' + store_name + '.jks',
                '-list',
                '-storepass',
                store_pass
            ]

            proc = Popen(cmd, stderr=PIPE, stdout=PIPE)
            stdout, stderr = proc.communicate()

            assert proc.wait() == 0
            assert re.search(cert_name + '-cert', stdout.decode())
            assert re.search('PrivateKeyEntry', stdout.decode())
