# fq run patient-survival-graph    '/ResearchStudy?identifier=TCGA-BRCA'
import pathlib


def test_patient_survival_graph(fhir_base_urls, tmp_path):
    """
    Test the patient survival graph functionality.
    This test checks if the patient survival graph can be generated correctly
    for a given ResearchStudy identifier.
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
        assert False, result.stdout
