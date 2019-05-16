import os
import logging
from pathlib import Path

from subprocess import Popen, PIPE

log = logging.getLogger(__name__)


class KeystoreGenerator:
    """
    Generate `jks` keystores from `pem` certificate files.
    """

    def __init__(self, artifact_dir):
        # Directory where the artifacts, certificates are stored.
        self.artifact_dir = os.path.join(artifact_dir, '')

    def create_truststore(self, trusted_cert_paths, name='truststore',
                          password='not-relevant-for-security'):
        """
        Generate `jks` truststore.

        Args:
            trusted_cert_paths: Paths to trusted certificates to be placed in
            the truststore.
            name: Name of the truststore without the `.jks` extension. Default:
            `truststore`.
            password: Password to be used for the keystore. Default: `not-relevant-for-security`.

        Returns:
            Path to the created truststore.
        """
        store_path = self.artifact_dir + name + '.jks'

        for cert_path in trusted_cert_paths:
            alias = os.path.splitext(os.path.basename(cert_path))[0]
            cmd = [
                'keytool',
                '-keystore',
                str(store_path),
                '-import',
                '-alias',
                alias,
                '-file',
                str(cert_path),
                '-trustcacerts',
                '-storepass',
                password,
                '-noprompt'
            ]

            log.info('Creating Java TrustStore: {}'.format(' '.join(cmd)))
            proc = Popen(cmd, shell=False, stderr=PIPE, stdout=PIPE)
            stdout, stderr = proc.communicate()
            if proc.wait() != 0:
                raise Exception('{}{}'.format(
                    stdout.decode(),
                    stderr.decode()
                ))

        os.chmod(store_path, 0o600)
        return store_path

    def create_entitystore(self, cert_path, key_path, node_cert_path='', chain=False,
                           store_name='entitystore',
                           store_password='not-relevant-for-security'):
        """
        Generate `jks` entitystore to be used by a specific entity (server or
        client).

        Args:
            cert_path: Path to the certificate or certificate chain to be put
            in the keystore.
            key_path: Path to the key corresponding to the certificate in
            cert_path.
            node_cert_path: the node directory for which to store trust databases
            chain: Specifies if cert_path points to a certificate chain or not.
            Default: False
            store_name: Name of the keystore without the '.jks' extension.
            Default: `entitystore`.
            store_password: Password to be used for the keystore. Default:
            `not-relevant-for-security`.

        Returns:
            Path to the created keystore.
        """

        java_store_file = store_name + '.jks'
        base_path = Path(self.artifact_dir) / node_cert_path
        java_store_path = base_path / java_store_file
        pkcs12_store_path = Path(str(java_store_path) + '.p12')  # trust.jks.p12
        certificate_alias = cert_path.name.split('.')[0]

        pkcs12_cmd = [
            'openssl',
            'pkcs12',
            '-export',
            '-in',
            str(cert_path),
            '-inkey',
            str(key_path),
            '-out',
            str(pkcs12_store_path),
            '-name',
            certificate_alias,
            '-passout',
            'pass:' + store_password
        ]

        if chain:
            pkcs12_cmd.extend([
                '-CAfile',
                str(cert_path),
                '-chain'
            ])

        log.info('Creating pkcs12 {} keystore: {}'.format(
            store_name,
            ' '.join(pkcs12_cmd)
        ))

        proc = Popen(pkcs12_cmd, shell=False, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        if proc.wait() != 0:
            raise Exception('{}{}'.format(
                stdout.decode(),
                stderr.decode()
            ))

        keystore_cmd = [
            'keytool',
            '-importkeystore',
            '-destkeystore',
            str(java_store_path),
            '-srckeystore',
            str(pkcs12_store_path),
            '-srcstoretype',
            'pkcs12',
            '-alias',
            certificate_alias,
            '-srcstorepass',
            store_password,
            '-deststorepass',
            store_password,
            '-noprompt'
        ]

        log.info('Creating jks {} keystore: {}'.format(
            store_name,
            ' '.join(pkcs12_cmd)))

        proc = Popen(keystore_cmd, shell=False, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        if proc.wait() != 0:
            raise Exception('{}{}'.format(
                stdout.decode(),
                stderr.decode()
            ))

        try:
            os.remove(pkcs12_store_path)
        except OSError:
            log.error('Could not remove pcks12 {} keystore: {}'.format(
                store_name,
                ' '.join(pkcs12_cmd)
            ))

        os.chmod(java_store_path, 0o600)
        return java_store_path
