from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_FIXTURES_DIR = Path(__file__).resolve().parent / "csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def csv_dir():
    return CSV_FIXTURES_DIR


@pytest.fixture
def data_dir(project_root):
    return project_root / "data"
