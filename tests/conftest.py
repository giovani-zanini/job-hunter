"""Load test configuration before importing the application."""

from pathlib import Path

import pytest
from dotenv import load_dotenv


def pytest_configure(config: pytest.Config) -> None:
    load_dotenv(Path(__file__).parent.parent / ".env.test", override=False)
