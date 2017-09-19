import pytest
import os
from tempfile import TemporaryDirectory

from exhibitor_tls_artifacts.gen_certificates import CertificateGenerator


class TestGenCertificates:
    """
    Tests how different certificate generation scenarios are handled by the
    CertificateGenerator class.
    """

    def test_default_certificate(self):
        with TemporaryDirectory() as test_dir:
            gen = CertificateGenerator(artifact_dir=test_dir)
            cert_path, key_path = gen.get_cert()

            assert gen.load_cert(cert_path) != None
            assert os.path.basename(cert_path) == 'entity-cert.pem'

            assert gen.load_key(key_path) != None
            assert os.path.basename(key_path) == 'entity-key.pem'

    @pytest.mark.parametrize('key_pass', [None, b'changeme'])
    def test_ca_certificate(self, key_pass):
        with TemporaryDirectory() as test_dir:
            gen = CertificateGenerator(artifact_dir=test_dir)
            cert_path, key_path = gen.get_cert(
                cert_name='no-ca',
                key_pass=key_pass,
                sa_names=['custom', '0.0.0.0']
            )

            assert gen.load_cert(cert_path) != None
            assert os.path.basename(cert_path) == 'no-ca-cert.pem'

            assert gen.load_key(key_path, key_pass) != None
            assert os.path.basename(key_path) == 'no-ca-key.pem'

    @pytest.mark.parametrize('entity_pass', [None, b'changeme'])
    @pytest.mark.parametrize('issuer_pass', [None, b'changeme'])
    def test_no_ca_certificate(self, entity_pass, issuer_pass):
        with TemporaryDirectory() as test_dir:
            gen = CertificateGenerator(artifact_dir=test_dir)
            issuer_cert_path, issuer_key_path = gen.get_cert(
                cert_name='issuer',
                key_pass=issuer_pass,
                sa_names=['issuer', '0.0.0.0']
            )

            issuer = (
                issuer_cert_path,
                issuer_key_path,
                issuer_pass
            )

            entity_cert_path, entity_key_path = gen.get_cert(
                cert_name='entity',
                key_pass=entity_pass,
                sa_names=['entity', '0.0.0.1'],
                issuer=issuer
            )

            assert gen.load_cert(entity_cert_path) != None
            assert os.path.basename(entity_cert_path) == 'entity-cert.pem'

            assert gen.load_key(entity_key_path, entity_pass) != None
            assert os.path.basename(entity_key_path) == 'entity-key.pem'
