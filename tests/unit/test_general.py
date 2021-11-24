"""Test Helper functions."""
import os
import pathlib
from unittest.mock import patch

from nornir_hier_config.utilities import check_file, create_folder, write_output

TEST_FOLDER = "tests/data/test_folder_success"


# Test Create Folder


def test_create_folder(test_folder):
    """Test create_folder success."""
    create_folder(test_folder)
    assert os.path.exists(test_folder)


def test_create_folder_exists(test_folder):
    """Test create_folder already exists success."""
    create_folder(test_folder)
    assert os.path.exists(test_folder)


@patch("os.makedirs", side_effect=OSError)
def test_create_folder_exception(os_mock, test_folder):
    """Test create_folder failure."""
    folder = f"{test_folder}/test"
    create_folder(folder)

    # using pathlib as we patched OS
    path = pathlib.Path("folder")
    assert not path.exists()


# Test Write Output


def test_write_output_success_new_path(test_folder):
    """Test write output success."""
    test_folder = f"{test_folder}/folder"
    write_output("test-text", test_folder, "file-name")
    assert os.path.exists(f"{test_folder}/file-name.txt")


def test_write_output_success_already_exists(test_folder):
    """Test write output success."""
    write_output("test-text", test_folder, "file-name")
    assert os.path.exists(f"{test_folder}/file-name.txt")


# Test Check File


def test_check_file():
    """Test false check_file."""
    assert not check_file("somebadpath.fail")
