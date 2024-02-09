import pytest
import json

from common import utils

from unittest.mock import patch, mock_open


def test_get_database_url_from_alembic_config(tmp_path):
    # Create a temporary Alembic configuration file
    alembic_config_file = tmp_path / "alembic.ini"
    with open(alembic_config_file, "w") as f:
        f.write("[alembic]\nsqlalchemy.url = sqlite:///test.db\n")

    # Call the method with the temporary Alembic configuration file path
    database_url = utils.get_database_url_from_alembic_config(alembic_config_file)

    # Assert that the database URL is correct
    assert database_url == "sqlite:///test.db"


def test_get_database_url_from_alembic_config_missing_url(tmp_path):
    # Create a temporary Alembic configuration file without the URL
    alembic_config_file = tmp_path / "alembic.ini"
    with open(alembic_config_file, "w") as f:
        f.write("[alembic]\n")

    # Call the method with the temporary Alembic configuration file path
    # and expect a ValueError to be raised
    with pytest.raises(ValueError):
        utils.get_database_url_from_alembic_config(alembic_config_file)


def test_load_valid_config():
    config_file_path = "test_config.json"
    config_data = """
    {
        "url": "http://www.omdbapi.com/",
        "parameters_global_search": {
            "apikey": "88888888",
            "page": 1,
            "s": "movie_title",
            "type": "movie"
        },
        "headers": {"Accepts": "application/json"},
        "parameters_featch_by_id": {"apikey": "88888888", "i": null}
    }
    """

    # Mock the open function to return a file object with the config data
    with patch("builtins.open", mock_open(read_data=config_data)) as mocked_open:

        # Call the load_config method
        result = utils.load_config(config_file_path)

        # Check if the open function was called with the correct file path
        mocked_open.assert_called_once_with(config_file_path, "r")

        # Check if the result matches the expected configuration data
        assert result == json.loads(config_data)
