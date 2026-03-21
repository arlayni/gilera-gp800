# tests/test_cli.py
from click.testing import CliRunner
from gp800_tool.cli import main
from conftest import SAMPLE_MAP_TXT, SAMPLE_MAP_TXT_DANGEROUS

def test_parse_command(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text(SAMPLE_MAP_TXT)
    runner = CliRunner()
    result = runner.invoke(main, ["parse", str(p)])
    assert result.exit_code == 0
    assert "Fuel Map" in result.output

def test_validate_safe(tmp_path, schemas_dir):
    p = tmp_path / "test.txt"
    p.write_text(SAMPLE_MAP_TXT)
    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(p), "--schemas", str(schemas_dir)])
    assert result.exit_code == 0
    assert "BLOCKER" not in result.output

def test_validate_dangerous(tmp_path, schemas_dir):
    p = tmp_path / "test.txt"
    p.write_text(SAMPLE_MAP_TXT_DANGEROUS)
    runner = CliRunner()
    result = runner.invoke(main, ["validate", str(p), "--schemas", str(schemas_dir)])
    assert result.exit_code == 1  # non-zero = blockers found
    assert "BLOCKER" in result.output

def test_quickcheck_safe(tmp_path, schemas_dir):
    p = tmp_path / "test.txt"
    p.write_text(SAMPLE_MAP_TXT)
    runner = CliRunner()
    result = runner.invoke(main, ["quickcheck", str(p), "--schemas", str(schemas_dir)])
    assert result.exit_code == 0
    assert "GREEN" in result.output or "PASS" in result.output
