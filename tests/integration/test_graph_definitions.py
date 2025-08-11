import pathlib
import sqlite3


def count_rows_in_resources_table(db_path):
    """Count the number of rows in the resources table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM resources")
    row_count = cursor.fetchone()[0]
    conn.close()
    return row_count


def test_run_patient_survival_graph(fhir_base_urls, tmp_path):
    """Test search parameters."""
    from click.testing import CliRunner

    runner = CliRunner()
    from fhir_aggregator_client.cli import cli

    db_path = str(tmp_path / "fhir-graph.sqlite")
    total_rows = 0
    expected_row_count = 2330
    for base_url in fhir_base_urls:
        pathlib.Path(db_path).unlink(missing_ok=True)

        result = runner.invoke(
            cli,
            [
                "run",
                "--fhir-base-url",
                base_url,
                "--db-path",
                db_path,
                "patient-survival-graph",
                "/ResearchStudy?identifier=TCGA-BRCA",
            ],
        )

        assert result.exit_code == 0, result.output

        row_count = count_rows_in_resources_table(db_path)
        total_rows += row_count
        assert row_count == expected_row_count, f"{base_url}/ResearchStudy?identifier=TCGA-BRCA has {row_count} expected {expected_row_count}"
    assert total_rows == expected_row_count * len(fhir_base_urls), f"Total rows {total_rows} expected {expected_row_count * len(fhir_base_urls)}"