from setuptools import find_packages, setup

setup(
    name="TorradaEmpanada",
    version="0.0.1",
    author="Arnau Perich Iglesias",
    author_email="arnau.perichiglesias@gmail.com",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.3.0",
        "openai>=1.0.0",
        "PyYAML>=6.0",
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "sentence-transformers>=2.2.2"
    ],
)
