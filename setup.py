from setuptools import setup, find_packages


def parse_requirements(filename: str) -> list[str]:
    with open(filename, "r") as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name="fhir_aggregator_client",
<<<<<<< Updated upstream
    version="0.1.7",
    packages=find_packages(),
=======
    version="0.1.8",
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
>>>>>>> Stashed changes
    install_requires=parse_requirements("requirements.txt"),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='walsbr',
    author_email='walsbr@ohsu.edu',
    url='https://github.com/FHIR-Aggregator/fhir-query',
    extras_require={
        'dtale': ['dtale'],
    },
    entry_points={
        "console_scripts": [
            "fq=fhir_query:cli.cli",
        ],
    },
)
