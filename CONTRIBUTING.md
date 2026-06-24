# Contributing Guide

Thank you for considering contributing to our Python project! By contributing, you help make our project better for everyone. Before you get started, please take a moment to review the following guidelines.

## Getting Started

1. **Fork the Repository:** Start by forking our project repository to your GitHub account. This will create a copy of the project under your account.

2. **Clone the Repository:** Clone the forked repository to your local machine using the following command:

```bash
git clone https://github.com/FHIR-Aggregator/fhir-query
python3 -m venv venv ; source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```
**Install Dependencies**: Ensure you have the necessary dependencies installed.
The installation process will install fhir query utility, see [how to configure it](https://aced-idp.github.io/getting-started/).

**Verify installation**: Run the following command to verify the installation:

```bash
g3t ping
msg: 'Configuration OK: Connected using profile:xxxx'
endpoint: https://aced-idp.org
username: your-email@institution.edu
```

### Running the notebooks

The notebooks under [`notebooks/`](notebooks/) need Jupyter and a kernel, which are
not part of the runtime dependencies. Install them via the `notebook` extra — ideally
into a clean virtual environment so unrelated packages don't surface spurious warnings:

```bash
python3 -m venv venv ; source venv/bin/activate
pip install -e ".[notebook]"
jupyter lab notebooks/fhir_aggregator.ipynb
```

### Making Changes


Create a Branch: Before making changes, create a new branch for your feature or bug fix:

```bash
git checkout -b feature-name
```

Write Code: Make your code changes, keeping the coding style and project conventions in mind.

Write Tests: If applicable, write tests for your code changes to ensure they work as expected.

```bash
pytest tests/ --cov=fhir_query

```

Check for Style: Run any code formatting tools or linters to maintain a consistent code style.

* pre commit tests

A reasonable set of checks, including running unit tests prior to each commit.  You can run these tests on demand by:

```
$ pre-commit install

$ pre-commit run --all-files
debug statements (python)................................................Passed
check python ast.........................................................Passed
fix utf-8 byte order marker..............................................Passed
check json...........................................(no files to check)Skipped
detect private key.......................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
check that scripts with shebangs are executable..........................Passed
check for case conflicts.................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
run our unit tests.......................................................Passed

```

Commit Changes: Commit your changes with a clear and concise commit message:

```bash
git commit -m "Add feature X" -m "Fixes #123"
```

Push Changes: Push your changes to your forked repository:

```bash
git push origin feature-name
```
### Opening a Pull Request
Create a Pull Request: Open a pull request on the original repository. Provide a clear title and description of your changes.

Review Process: Participate in discussions and address feedback. Make additional commits if necessary.

Code Review: The project maintainers will review your code. Be prepared to make further changes if needed.

Merge: Once approved, your pull request will be merged. Congratulations!

Code of Conduct
Please note that our project has a Code of Conduct. We expect all contributors to adhere to its guidelines to ensure a positive and inclusive community.

Thank you for contributing to our project! Your efforts are highly appreciated. If you have any questions or need assistance, feel free to reach out to us.

## Distribution

Releases to [PyPI](https://pypi.org/project/fhir-aggregator-client/) are published
automatically by the [`Publish to PyPI`](.github/workflows/publish.yml) GitHub Action
whenever a `v*` tag is pushed. The action builds the sdist and wheel, uploads them
using [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — so
no API tokens or passwords need to be stored or exported — and creates a matching
[GitHub Release](https://github.com/FHIR-Aggregator/fhir-aggregator-client/releases)
with the built artifacts attached.

The package version is derived from the git tag by
[`setuptools-scm`](https://setuptools-scm.readthedocs.io/) (configured in
[`pyproject.toml`](pyproject.toml)). There is **no version string to edit** — the tag
is the single source of truth, and `fq --version` reports whatever was tagged.

### Cutting a release

```
git checkout development && git pull
git tag v0.2.4
git push origin v0.2.4
```

That's it: the tag triggers the build, the PyPI upload, and the GitHub Release.

### Pre-releases

Use a [PEP 440](https://peps.python.org/pep-0440/) pre-release tag (`rc`, `a`, or `b`):

```
git tag v0.3.0rc1
git push origin v0.3.0rc1
```

The workflow marks it as a pre-release on GitHub, and PyPI marks it as a pre-release
automatically: a plain `pip install fhir-aggregator-client` skips it, and users opt in
with

```
pip install --pre fhir-aggregator-client   # or pin: ==0.3.0rc1
```

### Building locally (optional)

To produce the distribution artifacts on your machine without publishing:

```
rm -rf build/ dist/
python -m build
twine check dist/*
```

### Manual release (fallback)

The tag-triggered workflow above is the normal path, but a maintainer can still
publish by hand (e.g. if CI is unavailable). Token-based `twine` uploads continue to
work alongside Trusted Publishing.

> **Important:** the version is derived from git by `setuptools-scm`, so **build from
> the tag**, not from a branch. Building from an untagged commit produces a development
> version like `0.2.4.post3` instead of the clean `0.2.4` you intend.

```sh
# 1. Create and push the tag (or check out an existing one)
git checkout development && git pull
git tag v0.2.4
git push origin v0.2.4

# 2. Build FROM the tag so setuptools-scm resolves a clean version
git checkout v0.2.4
rm -rf build/ dist/
python -m build
twine check dist/*

# 3. Upload (uses your PyPI API token; see
#    https://twine.readthedocs.io/en/stable/#environment-variables)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...
twine upload dist/*
```

Avoid publishing the same version both manually and via the workflow — PyPI rejects
duplicate uploads of an existing version.

