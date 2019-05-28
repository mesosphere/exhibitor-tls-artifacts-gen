import datetime
import os
import ipaddress

from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


class CertificateGenerator:
    """
    Generate `x509` certificates in `pem` format.
    """

    def __init__(self,
                 artifact_dir,
                 country='US',
                 state='CA',
                 locality='San Francisco',
                 organization='Mesosphere'):
        # This adds trailing / to the path
        self.artifact_dir = os.path.join(artifact_dir, '')
        self.country = country
        self.state = state
        self.locality = locality
        self.organization = organization

    def load_cert(self, cert_path):
        with open(cert_path, "rb") as f:
            cert_data = f.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        return cert

    def __store_cert(self, cert, cert_path):
        cert_path.parent.mkdir(mode=0o700, exist_ok=True)
        with open(cert_path, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    def load_key(self, key_path, password=None):
        with open(key_path, "rb") as f:
            key_data = f.read()
            key = serialization.load_pem_private_key(data=bytes(key_data),
                                                     password=password,
                                                     backend=default_backend())

        return key

    def __store_key(self, key, key_path, password=None):
        key_path.parent.mkdir(mode=0o700, exist_ok=True)
        if password is None:
            encryption = serialization.NoEncryption()
        else:
            encryption = serialization.BestAvailableEncryption(password)

        with open(key_path, 'wb') as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=encryption))

        os.chmod(key_path, 0o600)

    def get_cert(self,
                 cert_name='entity',
                 node_cert_path='',
                 key_pass=None,
                 sa_names=None,
                 issuer=None):
        """
        Creates self signed CA certificates or end-entity certificates.

        Args:
            cert_name: Name of the certificate without `-cert` in the name or
            the `.pem` suffix.
            node_cert_path: The node specific directory for to store the cert
            key_pass: Password to use for the certificate key. Default:
            `None`.
            sa_names: List of IP addresses or DNS addresses to be used as
            `Subject Alternative Names` for the certificate. Default:
            `None`.
            issuer: (Certificate, Key, Password) triple for the issuer.
            If none is provided the certificate will be self signed.
            Default: `None`.
        """

        cert_file = cert_name + '-cert.pem'
        key_file = cert_name + '-key.pem'

        base_path = Path(self.artifact_dir) / node_cert_path

        cert_path = base_path / cert_file
        key_path = base_path / key_file

        cert_key = rsa.generate_private_key(public_exponent=65537,
                                            key_size=4096,
                                            backend=default_backend())

        self.__store_key(cert_key, key_path, key_pass)

        cert_subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, self.country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, self.locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.organization),
            x509.NameAttribute(NameOID.COMMON_NAME, cert_name),
        ])

        if sa_names is None:
            sa_names = ['localhost']

        if issuer is not None:
            issuer_cert = self.load_cert(issuer[0])
            cert_issuer_subject = issuer_cert.subject
            issuer_key = self.load_key(issuer[1],
                                       issuer[2] if len(issuer) > 2 else None)
        else:
            cert_issuer_subject = cert_subject
            issuer_key = cert_key

        cert = x509.CertificateBuilder().subject_name(cert_subject).issuer_name(
            cert_issuer_subject).public_key(
                cert_key.public_key()).serial_number(
                    x509.random_serial_number()).not_valid_before(
                        datetime.datetime.utcnow()).not_valid_after(
                            datetime.datetime.utcnow() +
                            datetime.timedelta(days=10 * 365))

        cert = cert.add_extension(
            x509.BasicConstraints(ca=True if issuer is None else False,
                                  path_length=None),
            critical=True,
        )

        converted_names = []
        for name in sa_names:
            try:
                converted_names.append(
                    x509.IPAddress(ipaddress.ip_address(name)))
            except ValueError:
                converted_names.append(x509.DNSName(name))

        cert = cert.add_extension(
            x509.SubjectAlternativeName(converted_names),
            critical=True,
        )

        cert = cert.sign(issuer_key, hashes.SHA256(), default_backend())

        self.__store_cert(cert, cert_path)

        return cert_path, key_path
