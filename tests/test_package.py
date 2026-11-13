"""Smoke test: the package installs and imports."""

import neural_recording_chain


def test_package_imports():
    assert neural_recording_chain.__version__
