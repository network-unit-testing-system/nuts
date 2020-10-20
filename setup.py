from setuptools import setup

setup(
    name="pytest-nuts",
    packages=["pytest_nuts"],
    # the following makes a plugin available to pytest
    entry_points={"pytest11": ["pytest_nuts=pytest_nuts.plugin"]},
    # custom PyPI classifier for pytest plugins
    classifiers=["Framework :: Pytest"],
)