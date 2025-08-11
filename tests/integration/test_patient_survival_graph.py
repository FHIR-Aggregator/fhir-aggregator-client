# fq run patient-survival-graph    '/ResearchStudy?identifier=TCGA-BRCA'
import pathlib

from fhir_aggregator_client.dataframer import RESEARCH_STUDY_MAP_WARNING


def test_patient_survival_graph(fhir_base_urls, tmp_path, caplog):
    """
    Test the patient survival graph functionality.
    This test checks if the patient survival graph can be generated correctly
    for a given ResearchStudy identifier.
    It also verifies that the expected log messages are generated.
    1. It runs the patient survival graph command with a specific ResearchStudy identifier.
    2. It checks if the command is executed successfully.
    3. It verifies that the expected log message "Study key not found for patient"
         appears exactly once in the logs.
    """
    from click.testing import CliRunner
    from fhir_aggregator_client.cli import cli
    db_path = str(tmp_path / "fhir-graph.sqlite")

    for base_url in fhir_base_urls:
        runner = CliRunner()
        pathlib.Path(db_path).unlink(missing_ok=True)
        result = runner.invoke(
            cli,
            [
                "run",
                "patient-survival-graph",
                "/ResearchStudy?identifier=TCGA-BRCA",
                "--fhir-base-url",
                base_url,
                "--db-path",
                db_path,
            ],
        )

        assert result.exit_code == 0, result.output
        result = runner.invoke(
            cli,
            ["results", "dataframe", "Patient"]
        )

        # check the logs for warnings
        # "Study key not found for patient" should only appear once
        assert result.exit_code == 0, result.output
        count = 0
        # read the logs

        for line in caplog.text.splitlines():
            if RESEARCH_STUDY_MAP_WARNING in line:
                count += 1
        assert count == 1, f"Expected '{RESEARCH_STUDY_MAP_WARNING}' to appear once, but found {count} times."
