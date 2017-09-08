import os
import logging

from subprocess import Popen, PIPE

log = logging.getLogger(__name__)


class KeystoreGenerator:
    """
    Generate `jks` keystores from `pem` certificate files.
    """

    def __init__(self, artifact_dir):
        # Directory where the artifacts, certificates are stored.
        self.artifact_dir = os.path.join(artifact_dir, '')

    def create_truststore(self, trusted_cert_paths,
                          name=u'truststore', password=u'changeme'):
        """
        Generate `jks` truststore.

        Args:
            trusted_cert_paths: Paths to trusted certificates to be placed in
            the truststore.
            name: Name of the truststore without the `.jks` extension. Default:
            `truststore`.
            password: Password to be used for the keystore. Default: `changeme`.
        
        Returns: 
            Path to the created truststore.
        """
        store_path = self.artifact_dir + name + '.jks'

        for cert_path in trusted_cert_paths:
            alias = os.path.splitext(os.path.basename(cert_path))[0]
            cmd = [
                'keytool',
                '-keystore',
                store_path,
                '-import',
                '-alias',
                alias,
                '-file',
                cert_path,
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
                    stdout.decode('utf-8'),
                    stderr.decode('utf-8')
                ))

        return store_path

    def create_entitystore(self, cert_path, key_path, key_password,
                           chain=False, store_name=u'entitystore',
                           store_password=u'changeme'):
        """
        Generate `jks` entitystore to be used by a specific entity (server or
        client).

        Args:
            cert_path: Path to the certificate or certificate chain to be put
            in the keystore.
            key_path: Path to the key corresponding to the certificate in
            cert_path.
            key_password: Password for the key in key_path.
            chain: Specifies if cert_path points to a certificate chain or not.
            Default: False
            store_name: Name of the keystore without the '.jks' extension.
            Default: `entitystore`.
            store_password: Password to be used for the keystore. Default:
            `changeme`.

        Returns:
            Path to the created keystore.
        """
        java_store_path = self.artifact_dir + '/' + store_name + '.jks'
        pkcs12_store_path = java_store_path + '.p12'
        certificate_alias = os.path.splitext(os.path.basename(cert_path))[0]

        pkcs12_cmd = [
            'openssl',
            'pkcs12',
            '-export',
            '-in',
            cert_path,
            '-inkey',
            key_path,
            '-out',
            pkcs12_store_path,
            '-name',
            certificate_alias,
            '-passout',
            'pass:' + store_password,
            '-passin',
            'pass:' + key_password
        ]

        if chain:
            pkcs12_cmd.extend([
                '-CAfile',
                cert_path,
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
                stdout.decode('utf-8'),
                stderr.decode('utf-8')
            ))

        keystore_cmd = [
            'keytool',
            '-importkeystore',
            '-destkeystore',
            java_store_path,
            '-srckeystore',
            pkcs12_store_path,
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
            ' '.join(pkcs12_cmd)
        ))

        proc = Popen(keystore_cmd, shell=False, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        if proc.wait() != 0:
            raise Exception('{}{}'.format(
                stdout.decode('utf-8'),
                stderr.decode('utf-8')
            ))

        try:
            os.remove(pkcs12_store_path)
        except OSError:
            log.error('Could not remove pcks12 {} keystore: {}'.format(
                store_name,
                ' '.join(pkcs12_cmd)
            ))

        return java_store_path
