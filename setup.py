from setuptools import setup, find_packages

VERSION = '0.3'

with open('requirements.txt') as requirements:
    INSTALL_REQUIRES = []
    for line in requirements.readlines():
        if not line.startswith('#'):
            INSTALL_REQUIRES.append(line)

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='exhibitor-tls-artifacts',
    packages=find_packages(),
    include_package_data=True,
    version=VERSION,
    description='Exhibitor TLS artifact generation script',
    long_description=LONG_DESCRIPTION,
    install_requires=INSTALL_REQUIRES,
    author='Mesosphere Inc.',
    author_email="security@mesosphere.com",
    url="https://mesosphere.com",
    keywords='exhibitor tls artifact mesosphere',
    entry_points={
        'console_scripts': [
            'exhibitor-tls-artifacts=exhibitor_tls_artifacts.gen_artifacts:app'
        ],
    },
)
