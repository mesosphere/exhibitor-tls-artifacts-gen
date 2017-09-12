import datetime
import os
import ipaddress

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


class CertificateWrapper:
    """
    Wrapper that makes it easier to work with `x509` certificates.
    """

    def __init__(self, cert_path, key_path):
        # Open certificates and keys and store the relevant information.
        with open(cert_path, "rb") as f:
            cert_data = f.read()
            self.cert = x509.load_pem_x509_certificate(
                cert_data,
                default_backend()
            )

        self.cert_path = cert_path

        with open(key_path, "rb") as f:
            key_data = f.read()
            self.key = serialization.load_pem_private_key(
                data=bytes(key_data),
                password=None,
                backend=default_backend()
            )

        self.key_path = key_path


class CertificateGenerator:
    """
    Generate `x509` certificates in `pem` format.
    """

    def __init__(self, artifact_dir, country='US', state='CA',
                 locality='San Francisco', organization='Mesosphere'):
        # This adds trailing / to the path
        self.artifact_dir = os.path.join(artifact_dir, '')
        self.country = country
        self.state = state
        self.locality = locality
        self.organization = organization

    def get_cert(self, cert_name='entity', sa_names=None, issuer=None):
        """
        Creates self signed CA certificates or end-entity certificates.

        Args:
            cert_name: Name of the certificate without `-cert` in the name or
            the `.pem` suffix.
            sa_names: List of IP addresses or DNS addresses to be used as
            `Subject Alternative Names` for the certificate. Default:
            `['localhost']`.
            issuer: CertificateWrapper containing the issuing certificate. If
            none is provided the certificate will be self signed. Default:
            `None`.
        """
        cert_path = self.artifact_dir + cert_name + '-cert.pem'
        key_path = self.artifact_dir + cert_name + '-key.pem'

        cert_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

        with open(key_path, 'wb') as f:
            f.write(cert_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

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
            cert_issuer = issuer.cert.subject
            issuer_key = issuer.key
        else:
            cert_issuer = cert_subject
            issuer_key = cert_key

        cert = x509.CertificateBuilder().subject_name(
            cert_subject
        ).issuer_name(
            cert_issuer
        ).public_key(
            cert_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=10 * 365)
        )

        if issuer is None:
            cert = cert.add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )

        converted_names = []
        for name in sa_names:
            try:
                converted_names.append(
                    x509.IPAddress(
                        ipaddress.ip_address(name)
                    )
                )
            except ValueError:
                converted_names.append(x509.DNSName(name))

        cert = cert.add_extension(
            x509.SubjectAlternativeName(converted_names),
            critical=True,
        )

        cert = cert.sign(issuer_key, hashes.SHA256(), default_backend())

        with open(cert_path, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        return CertificateWrapper(cert_path, key_path)
