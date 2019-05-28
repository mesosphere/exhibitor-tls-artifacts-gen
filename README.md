[![Build Status](https://travis-ci.com/rdeliallisi/exhibitor-tls-artifacts-gen.svg?token=zXsAbFGfuomQQchMVUL3&branch=master)](https://travis-ci.com/rdeliallisi/exhibitor-tls-artifacts-gen)

# Exhibitor TLS Artifact Generation

Generate `TLS` artifacts used by `Admin Router` and `Exhibitor`. The
created artifacts, if placed in specific locations on a`DC/OS Enterprise`
master node, secure the `Exhibitor` ensemble. This is achieved by making
each `Exhibitor` node talk `TLS` to the other using the artifacts generated
by this script. `Admin Router` is the only instance, other than `Exhibitor`
that can pick up these artifacts and talk to the ensemble.

* [System Requirements](#system-requirements)
* [Installation](#installation)
* [Script Usage](#script-usage)
* [Artifact Usage](#artifact-usage)
* [Tests](#tests)

## System Requirements
1) `Python 3.5+` must be installed.
2) `Java 8` must be installed.
3) `OpenSSL 1.x.y` must be installed.

## Installation

To keep your global python environment clean, we suggest creating a virtual
environment using `virtualenv`.

1) Install `virtualenv` run the following:
    ```sh
    pip install virtualenv
    ```

2) Create a virtual environment (`Python3.6` is required) :
    ```sh
    virualenv -p python3.6 <name of environment>
    ```

To install the `exhibitor-tls-artifacts` package, from the same directory as
this file, run the following:
```sh
pip install --editable .
```

## Docker image

This script is published as a docker container under `mesosphere/exhibitor-tls-artifacts-gen`
repository. It is possible to launch this script without installing Python, OpenSSL or Java
dependencies with docker:

```
docker run -it --rm -v $(pwd):/build --workdir /build mesosphere/exhibitor-tls-artifacts-gen --help
```

For convenience, a bash script can be downloaded from the GitHub release page and invoked directly.

```sh
curl -O https://github.com/mesosphere/exhibitor-tls-artifacts-gen/releases/latest/download/exhibitor-tls-artifacts
chmod +x exhibitor-tls-artifacts
./exhibitor-tls-artifacts -- --help
```

There is a limitation when using the `exhibitor-tls-artifacts` bash script.
The output of running this script is a directory that contains TLS artifacts (certificates, private keys and root CA certificate).
The script mounts current working directory the container with the script.
Only paths relative to the current working directory can be used as `--output-directory`.
Using absolute path will result in artifacts being generated in the container and destroyed when container exits.

If it is necessary to store the artifacts in a directory other than the current working directory
the bash script can take an extra parameter  `-b, --bind-directory`. For example:

```
$ ./exhibitor-tls-artifacts -b /tmp 192.168.0.1 192.168.0.2 192.168.0.3

$ sudo tree /tmp/artifacts/
/tmp/artifacts/
├── node_192_168_0_1
│   ├── client-cert.pem
│   ├── client-key.pem
│   ├── clientstore.jks
│   ├── root-cert.pem
│   ├── serverstore.jks
│   └── truststore.jks
├── node_192_168_0_2
│   ├── client-cert.pem
│   ├── client-key.pem
│   ├── clientstore.jks
│   ├── root-cert.pem
│   ├── serverstore.jks
│   └── truststore.jks
├── node_192_168_0_3
│   ├── client-cert.pem
│   ├── client-key.pem
│   ├── clientstore.jks
│   ├── root-cert.pem
│   ├── serverstore.jks
│   └── truststore.jks
├── root-cert.pem
└── truststore.jks

3 directories, 20 files

```

## Script Usage

```sh
Usage: exhibitor-tls-artifacts [OPTIONS] [NODES]...

  Generates Admin Router and Exhibitor TLS artifacts. NODES should consist
  of a space seperated list of master ip addresses. See
  https://docs.mesosphere.com/1.13/security/ent/tls-ssl/exhibitor-tls/

Options:
  -d, --output-directory TEXT  Directory to put artifacts in. This
                               output_directory must not exist.
  --help                       Show this message and exit.
```

## Artifact Usage

All artifacts are found in `./artifacts` or in the user specified directory. This
tool creates sub-directories for each `NODE`. If the node ip address is `10.10.10.10`,
the artifacts for that node will land in `<artifacts_dir>/node_10_10_10_10/`.

* `clientstore.jks`
    * Contains `client-cert.pem` and `client-key.pem`.
    * Is used by `Exhibitor` instances to present client certificates.
* `client-cert.pem` and `client-key.pem`
    * Are used by `Admin Router` as client (certificate, key) pair to talk to
    `Exhibitor`.
* `serverstore.jks`
    * Contains `server-cert.pem` and `server-key.pem`.
    * Is used by `Exhibitor` instances to present server certificates.
* `truststore.jks`
    * Contains `root-cert.pem`.
    * Is used by `Exhibitor` to verify presented certificates (client and
    server).
* `root-cert.pem`
    * Is used by `Admin Router` to verify `Exhibitor` server certificates.

## Tests

To run the tests first follow the instructions under
[Installation](#installation) to get all the required dependencies. Then run:

```sh
make test
```

## Release

A release is created by making new git tag that should match version in `setup.py` file.
When a new tag is pushed to the main repo the CI will make a build and create a new release in GitHub.
A tag should be pointing to a commit that has been merged to `master` branch.

Example:

```sh
git tag v0.2
git push --tags
```
