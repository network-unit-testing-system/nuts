from pathlib import Path
from typer.testing import CliRunner
from nornir import InitNornir
from nuts.nuts_init import app

runner = CliRunner()


def test_app(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--test-dir",
            str(tmp_path / "tests"),
            "--nornir-config",
            str(tmp_path / "nr_config.yaml"),
            "--inventory-dir",
            str(tmp_path / "inventory"),
            "--create-simple-inventory",
            "--cisco-xe",
            "--juniper-junos",
            "--arista-eos",
            "--cisco-nxos",
            "--cisco-xr",
            "--netmiko-session-logs",
        ],
    )
    assert result.exit_code == 0

    nr = InitNornir(config_file=str(tmp_path / "nr_config.yaml"))
    assert len(nr.inventory.hosts) == 5
