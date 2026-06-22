import asyncio
import json
import logging
import os
import pathlib
import sys
import tempfile

import click
import pandas as pd
import requests
import yaml
from fhir.resources.graphdefinition import GraphDefinition
from halo import Halo
from tabulate import tabulate

from fhir_aggregator_client import GraphDefinitionRunner, setup_logging, ensure_our_directory
from fhir_aggregator_client.dataframer import Dataframer
from fhir_aggregator_client.visualizer import visualize_aggregation
from fhir_aggregator_client.vocabulary import vocabulary_simplifier
from fhir_aggregator_client.graph_definition import ls as ls_graph_definitions

DEFAULT_LOG_FILE = pathlib.Path(ensure_our_directory()) / "app.log"
FHIR_BASE_ENV_VAR = "FHIR_BASE"

DB_PATH_ENV_VAR = "FHIR_DB_PATH"
DEFAULT_DB_PATH = pathlib.Path(ensure_our_directory()) / "fhir-graph.sqlite"
DEFAULT_VISUALIZATION_PATH = "fhir-graph.html"
DEFAULT_TSV_PATH = "fhir-graph.tsv"


def _atomic_write_text(output_path: str, text: str) -> None:
    """Write text to output_path via a temp file, moving into place only on success.

    Ensures a failed render never leaves a partial or empty file at output_path.
    """
    path = pathlib.Path(output_path)
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(path.parent) if str(path.parent) else ".",
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    try:
        with tmp:
            tmp.write(text)
        os.replace(tmp.name, output_path)
    except Exception:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise


class CustomDefaultGroup(click.Group):
    def list_commands(self, ctx):
        # def natural_keys(text):
        #     return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]
        # return sorted(self.commands.keys(), key=natural_keys)
        return ["ls", "run", "results", "vocabulary"]


@click.group(cls=CustomDefaultGroup)
@click.version_option()
def cli():
    """FHIR-Aggregator utilities."""
    pass


@cli.command()
@click.option(
    "--fhir-base-url",
    required=True,
    help=f"Base URL of the FHIR server. default: env ${FHIR_BASE_ENV_VAR}",
    envvar=FHIR_BASE_ENV_VAR,
)
@click.option("--format", "output_format", "-f", default="tsv", help="Output format", type=click.Choice(["tsv", "yaml", "json"]))
@click.option("--debug", is_flag=True, help="Enable debug mode.")
@click.option("--log-file", default=DEFAULT_LOG_FILE, help=f"Path to the log file. default={DEFAULT_LOG_FILE}")
@click.option(
    "--dtale",
    "launch_dtale",
    default=False,
    show_default=True,
    is_flag=True,
    help="Open the graph in a browser using the dtale package for interactive data exploration.",
)
@click.argument("output_path", required=False, default=None)
def vocabulary(
    fhir_base_url: str,
    output_path: str,
    debug: bool,
    log_file: str,
    output_format: str,
    launch_dtale: bool,
) -> None:
    """FHIR-Aggregator's key Resources and CodeSystems.
    \b

    OUTPUT_PATH: Path to the output file. If not provided, the output will be printed to stdout.
    """

    setup_logging(debug, log_file)

    if fhir_base_url.endswith("/"):
        fhir_base_url = fhir_base_url[:-1]

    try:
        with Halo(text="Collecting vocabularies", spinner="dots", stream=sys.stderr) as spinner:
            query_url = f"{fhir_base_url}/Observation?_count=1000&code=vocabulary&_include=Observation:focus"
            response = requests.get(query_url, timeout=300)
            response.raise_for_status()
            bundle = response.json()
            results = bundle

            if launch_dtale:
                click.secho("Rendering tsv output in browser using dtale", file=sys.stderr)
                output_format = "tsv"

            vocabulary_count = 0
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                component_list = resource.get("component", [])
                vocabulary_count += len(component_list)

            if not output_format in ["yaml", "json"]:
                results = vocabulary_simplifier(bundle)

            # Render the full output before touching the destination so a failed
            # query never leaves behind a missing or truncated output file.
            if launch_dtale:
                # TODO - add check that dtale is installed
                import dtale

                df = pd.DataFrame(results)
                spinner.succeed(f"Showing {len(results)} vocabularies in browser")
                dtale.show(df, subprocess=False, open_browser=True, port=40000)
                return

            if output_format == "yaml":
                rendered = yaml.dump(results, default_flow_style=False, sort_keys=False) + "\n"
                count = vocabulary_count
            elif output_format == "json":
                rendered = json.dumps(results, indent=2) + "\n"
                count = vocabulary_count
            else:
                rendered = pd.DataFrame(results).to_csv(sep="\t", index=False)
                count = len(results)

            if output_path is None:
                sys.stdout.write(rendered)
                destination = "stdout"
            else:
                _atomic_write_text(output_path, rendered)
                destination = output_path

            spinner.succeed(f"Wrote {count} vocabularies to {destination}")

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        if debug:
            raise e
        raise click.ClickException(str(e) or e.__class__.__name__)


@cli.command()
@click.option(
    "--format", "output_format", "-f", default="table", help="Output format", type=click.Choice(["table", "yaml", "json"])
)
def ls(output_format) -> None:
    """List all the installed GraphDefinitions."""
    if output_format == "table":
        rows = [[_["id"], _["description"]] for _ in ls_graph_definitions()]
        print(tabulate(rows, headers=["id", "description"], tablefmt="orgtbl"))
    elif output_format == "json":
        print(json.dumps(ls_graph_definitions(), indent=2))
    else:
        print(yaml.dump(ls_graph_definitions(), default_flow_style=False))


@cli.command()
@click.option(
    "--fhir-base-url",
    required=True,
    help=f"Base URL of the FHIR server. default: env ${FHIR_BASE_ENV_VAR}",
    envvar=FHIR_BASE_ENV_VAR,
)
@click.option(
    "--db-path",
    default=DEFAULT_DB_PATH,
    help=f"Path to sqlite database. default: {DEFAULT_DB_PATH} env: {DB_PATH_ENV_VAR}",
    envvar=DB_PATH_ENV_VAR,
)
@click.option(
    "--append",
    is_flag=True,
    default=False,
    show_default=True,
    help="Accumulate into an existing database instead of clearing it first. "
    "By default the database is reset so the reported counts reflect only this run.",
)
@click.option("--debug", is_flag=True, help="Enable debug mode.")
@click.option("--log-file", default=DEFAULT_LOG_FILE, help=f"Path to the log file. default={DEFAULT_LOG_FILE}")
@click.argument("graph-definition", required=True)
@click.argument("fhir-query", required=True)
def run(
    graph_definition: str,
    fhir_query: str,
    fhir_base_url: str,
    db_path: str,
    append: bool,
    log_file: str,
    debug: bool,
) -> None:
    """Run GraphDefinition queries.

    GRAPH_DEFINITION is the path|id of a GraphDefinition file.
    \nFHIR_QUERY the query to start traversal.
    """

    setup_logging(debug, log_file)

    if fhir_base_url.endswith("/"):
        fhir_base_url = fhir_base_url[:-1]

    if not graph_definition:
        raise click.UsageError("You must provide a graph_definition.")

    if not fhir_query:
        raise click.UsageError("You must provide a fhir_query.")

    db_exists = pathlib.Path(db_path).exists()

    runner = GraphDefinitionRunner(fhir_base_url, db_path, debug)

    if db_exists:
        if append:
            click.secho(
                f"warning: Appending to existing database at {db_path}. "
                "Reported counts will include resources from previous runs.",
                file=sys.stderr,
                fg="yellow",
            )
        else:
            click.secho(
                f"Clearing existing database at {db_path} (use --append to accumulate instead).",
                file=sys.stderr,
                fg="yellow",
            )
            runner.reset()

    async def run_runner() -> None:
        graph_definitions = ls_graph_definitions()
        graph_definition_file_path = None

        # they provided a path to a file
        if pathlib.Path(graph_definition).exists():
            graph_definition_file_path = graph_definition

        # they provided an id of a graph definition
        if graph_definition in [gd["id"] for gd in graph_definitions]:
            graph_definition_file_path = [gd["path"] for gd in graph_definitions if gd["id"] == graph_definition][0]

        if graph_definition_file_path:
            with open(graph_definition_file_path, "r") as f:
                if graph_definition_file_path.endswith(".yaml") or graph_definition_file_path.endswith(".yml"):
                    graph_definition_dict = yaml.safe_load(f)
                else:
                    graph_definition_dict = json.load(f)
        else:
            # they provided an id of a graph definition on the server
            graph_definition_dict = await runner.fetch_graph_definition(graph_definition)

        _ = GraphDefinition(**graph_definition_dict)
        click.echo(f"{_.id} is valid FHIR R5 GraphDefinition", file=sys.stderr)

        logging.debug(runner.db_path)
        spinner = Halo(text=f"Running {_.id} traversal", spinner="dots", stream=sys.stderr)
        try:
            await runner.run(graph_definition_dict, fhir_query, spinner)
        finally:
            spinner.stop()
        click.echo(f"Aggregated Results: {runner.count_resource_types()}", file=sys.stderr)
        click.echo(f"database available at: {runner.db_path}", file=sys.stderr)

    try:
        asyncio.run(run_runner())
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        click.echo(f"Error: {e}", file=sys.stderr)
        if debug:
            raise e


@cli.group()
def results():
    """Work with the results of a GraphDefinition query."""
    pass


@results.command(name="visualize")
@click.option(
    "--db-path",
    default=DEFAULT_DB_PATH,
    help=f"Path to sqlite database. default: {DEFAULT_DB_PATH} env: {DB_PATH_ENV_VAR}",
    envvar=DB_PATH_ENV_VAR,
)
@click.option(
    "--ignored-edges",
    "-i",
    multiple=True,
    help="Edges to ignore in the visualization default=part-of-study",
    default=["part-of-study"],
)
@click.argument("output_path", type=click.File("w"), required=False, default=DEFAULT_VISUALIZATION_PATH)
def visualize(db_path: str, output_path: click.File, ignored_edges: list[str]) -> None:
    """Visualize the FHIR Resources in the database.

    \b
    OUTPUT_PATH: Path to the output file. If not provided, the output will be written to ./fhir-graph.html.
    """
    from fhir_aggregator_client import ResourceDB

    try:
        db = ResourceDB(db_path=db_path)
        visualize_aggregation(db.aggregate(ignored_edges), output_path.name)
        click.echo(f"Wrote: {output_path.name}", file=sys.stderr)
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        click.echo(f"Error: {e}", file=sys.stderr)


@results.command(name="summarize")
@click.option(
    "--db-path",
    default=DEFAULT_DB_PATH,
    help=f"Path to sqlite database. default: {DEFAULT_DB_PATH} env: {DB_PATH_ENV_VAR}",
    envvar=DB_PATH_ENV_VAR,
)
def summarize(db_path: str) -> None:
    """Summarize the aggregation results."""
    from fhir_aggregator_client import ResourceDB

    try:
        db = ResourceDB(db_path=db_path)
        yaml.dump(json.loads(json.dumps(db.aggregate())), sys.stdout, default_flow_style=False)

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        click.echo(f"Error: {e}", file=sys.stderr)
        # raise e


@results.command(name="dataframe")
# TODO - fix the default paths
@click.option(
    "--db-path",
    default=DEFAULT_DB_PATH,
    help=f"Path to sqlite database. default: {DEFAULT_DB_PATH} env: {DB_PATH_ENV_VAR}",
    envvar=DB_PATH_ENV_VAR,
)
@click.option(
    "--dtale",
    "launch_dtale",
    default=False,
    show_default=True,
    is_flag=True,
    help="Open the graph in a browser using the dtale package for interactive data exploration.",
)
@click.argument(
    "data_type",
    required=True,
    type=click.Choice(["Specimen", "DocumentReference", "ResearchSubject", "Patient"]),
    default="Specimen",
)
@click.argument("output_path", type=click.File("w"), required=False, default=DEFAULT_TSV_PATH)
def dataframe(db_path: str, output_path: click.File, launch_dtale: bool, data_type: str) -> None:
    """Create dataframe from the local db.
    \b
    OUTPUT_PATH: Path to the output file. If not provided, the output will be written to ./fhir-graph.tsv
    """

    try:
        db = Dataframer(db_path=db_path)
        # TODO - add more data types - including condition
        assert data_type in ["Specimen", "Patient"], f"Sorry {data_type} dataframe is not supported yet."

        df: pd.DataFrame | None = None
        if data_type == "Specimen":
            df = pd.DataFrame(db.flattened_specimens())
        if data_type == "Patient":
            df = pd.DataFrame(db.flattened_patients())

        if launch_dtale:
            # TODO - add check that dtale is installed
            import dtale

            dtale.show(df, subprocess=False, open_browser=True, port=40000)
        elif df is not None:
            # export to tsv
            df.to_csv(output_path, sep="\t", index=False)
            click.secho(f"Saved {output_path.name}", file=sys.stderr)
        else:
            click.secho(f"No data found for {data_type}", file=sys.stderr)

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        click.echo(f"Error: {e}", file=sys.stderr)
        # raise e


if __name__ == "__main__":
    cli()
