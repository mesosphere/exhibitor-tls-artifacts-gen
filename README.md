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

1) `Java 8` must be installed.
2) `OpenSSL 1.x.y` must be installed.

## Installation

To keep your global python environment clean, we suggest creating a virtual
environment using `virtualenv`.

1) Install `virtualenv` run the following:
    ```sh
    pip install virtualenv
    ```

2) Create a virtual environment (`Python3.4` is required) :
    ```sh
    virualenv -p python3.4 <name of environment>
    ```

To install the `exhibitor-tls-artifacts` package, from the same directory as
this file, run the following:
```sh
pip install --editable .
```

## Script Usage

```sh
exhibitor-tls-artifacts [OPTIONS] [SANS]...

Args:
    SANS: Subject Alternative Names to be put in the end-entity
              certificates. Can be DNS names or IP addresses.
Options:
  -d, --dir TEXT  Directory to put generated artifacts in.
                  Default: ./artifacts/ .
  --help          Show this message and exit.
```

## Artifact Usage

All artifacts are found in `./artifacts/` or in the user specified directory.

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
pytest
```
