import json
from alembic.config import Config


def get_database_url_from_alembic_config(alembic_config="alembic.ini"):
    """
    Get database URL from Alembic configuration.

    Args:
        alembic_config (str): The path to the Alembic configuration file.

    Returns:
        str: The database URL.
    """
    alembic_cfg = Config(alembic_config)
    database_url = alembic_cfg.get_section_option("alembic", "sqlalchemy.url")
    if database_url is None:
        raise ValueError(
            "Database URL is missing or could not be retrieved from Alembic configuration"
        )
    return database_url


def load_config(config_file_path="config.json"):
    """
    Load configuration from file.

    Args:
        config_file_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration.
    """
    with open(config_file_path, "r") as file:
        return json.load(file)
