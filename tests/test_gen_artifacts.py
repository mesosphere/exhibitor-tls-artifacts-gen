import stat
import textwrap
import re
from pathlib import Path

import click
import click.testing

from exhibitor_tls_artifacts.gen_artifacts import app


class TestCLI:

    @staticmethod
    def _validate_files(directory):
        """ Ensures that artifacts are created and that they have the
        appropriate permission """
        files = [('client-cert.pem', 0o100644), ('client-key.pem', 0o100600),
                 ('clientstore.jks', 0o100600), ('root-cert.pem', 0o100644),
                 ('serverstore.jks', 0o100600), ('truststore.jks', 0o100600)]
        for f, mode in files:
            full_path = directory / f
            assert full_path.exists()
            assert full_path.stat()[stat.ST_MODE] == mode

    def test_default(self):
        """ Tests the most basic operation """
        runner = click.testing.CliRunner()

        with runner.isolated_filesystem() as temp:
            temp_path = Path(temp)
            result = runner.invoke(app,
                                   args=['10.10.10.10'],
                                   catch_exceptions=False)

            assert result.exit_code == 0
            artifact_path = temp_path / 'artifacts' / '10.10.10.10'
            assert artifact_path.exists()
            self._validate_files(artifact_path)

    def test_custom_dir(self, tmp_path):
        """ Test outputting artifacts to a customer location """
        runner = click.testing.CliRunner()
        new_path = tmp_path / 'new'
        result = runner.invoke(app,
                               args=['-d', new_path, '10.10.10.10'],
                               catch_exceptions=False)

        assert result.exit_code == 0
        self._validate_files(new_path / '10.10.10.10')

    def test_dir_exists(self):
        """ Test error case when the output directory already exists """
        rgx = re.compile("^Error: Invalid value for \"-d\" / \"--output-directory\": "
                         "Artifacts location .* already exists\\.$")
        runner = click.testing.CliRunner()

        with runner.isolated_filesystem() as temp:
            temp_path = Path(temp)
            output_dir = temp_path / 'exists'
            output_dir.mkdir()
            result = runner.invoke(app,
                                   args=['-d', output_dir, '10.10.10.10'],
                                   catch_exceptions=False)
            assert result.exit_code == 2
            for line in result.stdout.splitlines():
                if rgx.match(line):
                    return
            raise Exception('CLI error output is incorrect: {}'.format(result.stdout))

    def test_no_nodes(self):
        """ Test error case if no arguments are provided """
        err = textwrap.dedent("""\
        Usage: exhibitor-tls-artifacts [OPTIONS] [NODES]...

        Error: No nodes have been provided.
        """)
        runner = click.testing.CliRunner()
        result = runner.invoke(app, catch_exceptions=False)
        assert result.exit_code == 2
        assert err == result.stdout

    def test_help(self):
        """ Tests if there are any changes to the help output. This
        is only useful for coercing a developer to write CLI tests if
        an option/argument is added. """
        expected_help = textwrap.dedent("""\
            Usage: exhibitor-tls-artifacts [OPTIONS] [NODES]...

              Generates Admin Router and Exhibitor TLS artifacts. NODES should consist of
              a space separated list of master ip addresses. See
              https://docs.mesosphere.com/1.13/security/ent/tls-ssl/exhibitor/

            Options:
              -d, --output-directory TEXT  Directory to put artifacts in. This
                                           output_directory must not exist.
              --help                       Show this message and exit.
            """)
        runner = click.testing.CliRunner()
        result = runner.invoke(app, args=['--help'])
        assert expected_help == result.stdout
