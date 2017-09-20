import pytest
import ipaddress

from tempfile import TemporaryDirectory
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding
from exhibitor_tls_artifacts.gen_certificates import CertificateGenerator


class TestGenCertificates:
    """
    Tests how different certificate generation scenarios are handled by the
    CertificateGenerator class.
    """

    def __verify_cert_signature(self, cert, key):
        key.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm
        )

    def __verify_cert_properties(self, cert, expected_dns_names,
                                 expected_ip_addr, expected_ca):
        sa_names = cert.extensions.get_extension_for_class(
            x509.SubjectAlternativeName
        ).value

        dns_names = sa_names.get_values_for_type(x509.DNSName)
        assert dns_names == expected_dns_names
        ip_addr = sa_names.get_values_for_type(x509.IPAddress)
        assert ip_addr == expected_ip_addr

        is_ca = cert.extensions.get_extension_for_class(
            x509.BasicConstraints
        ).value.ca
        assert is_ca == expected_ca

    def test_default_certificate(self):
        with TemporaryDirectory() as test_dir:
            gen = CertificateGenerator(artifact_dir=test_dir)
            cert_path, key_path = gen.get_cert()

            cert = gen.load_cert(cert_path)
            key = gen.load_key(key_path)

            self.__verify_cert_properties(cert, ['localhost'], [], True)
            self.__verify_cert_signature(cert, key)

    @pytest.mark.parametrize('key_pass', [None, b'changeme'])
    def test_ca_certificate(self, key_pass):
        with TemporaryDirectory() as test_dir:
            gen = CertificateGenerator(artifact_dir=test_dir)
            dns_names = ['localhost']
            ip_addr = [ipaddress.IPv4Address('127.0.0.1')]

            cert_path, key_path = gen.get_cert(
                cert_name='no-ca',
                key_pass=key_pass,
                sa_names=dns_names + ip_addr
            )

            cert = gen.load_cert(cert_path)
            key = gen.load_key(key_path, key_pass)

            self.__verify_cert_properties(cert, dns_names, ip_addr, True)
            self.__verify_cert_signature(cert, key)

    @pytest.mark.parametrize('entity_pass', [None, b'changeme'])
    @pytest.mark.parametrize('issuer_pass', [None, b'changeme'])
    def test_no_ca_certificate(self, entity_pass, issuer_pass):
        with TemporaryDirectory() as test_dir:
            gen = CertificateGenerator(artifact_dir=test_dir)
            dns_names = ['localhost']
            ip_addr = [ipaddress.IPv4Address('127.0.0.1')]

            issuer_cert_path, issuer_key_path = gen.get_cert(
                cert_name='issuer',
                key_pass=issuer_pass,
                sa_names=dns_names + ip_addr
            )

            issuer = (
                issuer_cert_path,
                issuer_key_path,
                issuer_pass
            )

            issuer_cert = gen.load_cert(issuer_cert_path)
            issuer_key = gen.load_key(issuer_key_path, issuer_pass)

            self.__verify_cert_properties(issuer_cert, dns_names, ip_addr,
                                          True)
            self.__verify_cert_signature(issuer_cert, issuer_key)

            entity_cert_path, entity_key_path = gen.get_cert(
                cert_name='entity',
                key_pass=entity_pass,
                sa_names=dns_names + ip_addr,
                issuer=issuer
            )

            entity_cert = gen.load_cert(entity_cert_path)
            entity_key = gen.load_key(entity_key_path, entity_pass)

            self.__verify_cert_properties(entity_cert, dns_names, ip_addr,
                                          False)
            self.__verify_cert_signature(entity_cert, issuer_key)

            with pytest.raises(InvalidSignature):
                self.__verify_cert_signature(entity_cert, entity_key)
