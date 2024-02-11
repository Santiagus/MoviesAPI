from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
import logging.config
import yaml

from common import utils


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for managing the lifespan of a FastAPI application.

    This context manager is typically used to handle setup and cleanup operations
    during the application's lifespan, such as initializing and closing connections
    or resources.

    Parameters:
        - `app` (FastAPI): The FastAPI application instance.

    Yields:
        - None: The async context manager yields control to the enclosed block.

    Example:
        ```python
        async with lifespan(my_app):
            # Perform setup operations here

        # Perform cleanup operations here, after the lifespan block exits
        ```
    """

    try:
        # Configure the root logger
        logging.basicConfig(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info(f"Service start. Loading configuration...")

        app.state.database_url = utils.get_database_url_from_alembic_config()

    except Exception as e:
        logging.error(f"An unexpected error occurred during startup: {e}")
    finally:
        yield
        # Shutdown (Close connections to db, ...)


app = FastAPI(title="Your API", version="1.0.0", lifespan=lifespan)

with open("movies_service/oas.yaml", "r") as file:
    oas_doc = yaml.safe_load(file)
app.openapi = lambda: oas_doc

from movies_service.api import api
