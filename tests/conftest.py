"""Conftest for Nornir Plugin Unit Tests."""
import os

import pytest
from nornir import InitNornir
from nornir.core.state import GlobalState

# pytest mark decorator to skip integration tests if INTEGRATION_TESTS=True
# These tests will connect to local lab environment to validate actual responses
# from locallly hosted network devices.
skip_integration_tests = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", True), reason="Do not run integration tests"
)

global_data = GlobalState(dry_run=True)
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# If NORNIR_LOG set to True, the log won't be deleted in teardown.
NORNIR_LOG = os.environ.get("NORNIR_LOG", False)


@pytest.fixture(scope="session", autouse=True)
def nornir():
    """Initialize nornir."""
    nr_nr = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": f"{DIR_PATH}/data/inventory_data/hosts.yml",
                "group_file": f"{DIR_PATH}/data/inventory_data/groups.yml",
                "defaults_file": f"{DIR_PATH}/data/inventory_data/defaults.yml",
            },
        },
        logging={"log_file": f"{DIR_PATH}/data/nornir_test.log", "level": "DEBUG"},
    )
    nr_nr.data = global_data
    return nr_nr


@pytest.fixture(scope="session", autouse=True)
def teardown_class():
    """Teardown the random artifacts created by pytesting."""
    if not NORNIR_LOG:
        nornir_logfile = f"{DIR_PATH}/data/nornir_test.log"
        if os.path.exists(nornir_logfile):
            os.remove(nornir_logfile)


@pytest.fixture(scope="function", autouse=True)
def reset_data():
    """Reset Data."""
    global_data.dry_run = True
    global_data.reset_failed_hosts()


@pytest.fixture(scope="session", autouse=True)
def test_folder():
    """Test folder."""
    return "tests/data/test_data/test_folder"


@pytest.fixture(scope="session", autouse=True)
def configs():
    """Config directories."""
    return f"{DIR_PATH}/data/configs"
