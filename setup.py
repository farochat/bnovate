"""Setup file."""

from setuptools import find_namespace_packages, setup

setup(
    name="bnovate",
    version="0.0.0",
    description="bNovate polygons",
    author="Fabien Rochat",
    author_email="fabien.a.rochat@gmail.com",
    packages=find_namespace_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "numpy",
        "pandas",
        "pyyaml",
        "flask",
        "psycopg2-binary",
        "shapely",
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "flake8",
            "flake8-bugbear",
            "pep8-naming",
            "flake8-docstrings",
            "pip-tools",
        ],
    },
)
