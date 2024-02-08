import aiohttp
import asyncio
import json
import logging
from requests import Session
from requests.exceptions import HTTPError
from sqlalchemy import create_engine
from alembic.config import Config
from data_layer.unit_of_work import UnitOfWork
from data_layer.movies_repository import MoviesRepository
from data_layer.models import MovieModel, Base


class MovieDataFetcher:
    """
    Class to fetch and save movie data.

    Attributes:
        config_file_path (str): The path to the configuration file.
        alembic_config (str): The path to the Alembic configuration file.
    """

    def __init__(
        self,
        config_file_path="data_fetcher/fetcher_config.json",
        alembic_config="alembic.ini",
    ):
        """
        Initializes the MovieDataFetcher.

        Args:
            config_file_path (str, optional): The path to the configuration file.
                Defaults to "data_fetcher/fetcher_config.json".
            alembic_config (str, optional): The path to the Alembic configuration file.
                Defaults to "alembic.ini".
        """
        self.config = self.load_config(config_file_path)
        self.database_url = self.get_database_url_from_alembic_config(alembic_config)
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)

    @staticmethod
    def load_config(config_file_path):
        """
        Load configuration from file.

        Args:
            config_file_path (str): The path to the configuration file.

        Returns:
            dict: The loaded configuration.
        """
        with open(config_file_path, "r") as file:
            return json.load(file)

    def get_database_url_from_alembic_config(self, alembic_config):
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

    @staticmethod
    def fetch_movies_data(url, parameters, headers, limit=100):
        """
        Fetch movie data from the OMDB API.

        Args:
            url (str): The URL of the OMDB API.
            parameters (dict): The parameters for the API request.
            headers (dict): The headers for the API request.
            limit (int, optional): The maximum number of movies to fetch. Defaults to 100.

        Returns:
            list: A list containing movie data fetched from the OMDB API.
        """
        logging.info("Data fetch started")
        session = Session()
        movies_data_list = [None] * limit
        PAGE_SIZE = 10
        pages = limit // PAGE_SIZE + 1
        for page in range(pages):
            parameters["page"] = page + 1
            response = session.get(url, headers=headers, params=parameters)
            logging.debug(f"Status code : {response.status_code}")
            logging.debug(f"Response : {response.text}")
            response.raise_for_status()
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("Response") != "True":
                    raise Exception(
                        f"Error ({response.status_code}) : {json_data.get('Error')}"
                    )
                json_data = response.json().get("Search")

                start = page * PAGE_SIZE
                end = (page + 1) * PAGE_SIZE
                movies_data_list[start:end] = json_data[:PAGE_SIZE]
                if limit <= end:
                    break
        logging.info(f"Read {len(movies_data_list)} movies.")
        return movies_data_list[:limit]

    @staticmethod
    async def fetch_movie_data_by_imdb_id(url, parameters, headers, imdb_id):
        """
        Fetch movie data by IMDb ID from the OMDB API.

        Args:
            url (str): The URL of the OMDB API.
            parameters (dict): The parameters for the API request.
            headers (dict): The headers for the API request.
            imdb_id (str): The IMDb ID of the movie.

        Returns:
            dict: Movie data fetched from the OMDB API.
        """
        parameters["i"] = imdb_id
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=headers, params=parameters)
            response_json = await response.json()

            logging.debug(f"Status code : {response.status}")
            logging.debug(f"Response : {response_json}")

            if response.status == 200:
                return response_json
            return None

    @staticmethod
    def camel_to_snake(name):
        """
        Convert camelCase string to snake_case.

        Args:
            name (str): The string to convert.

        Returns:
            str: The converted string in snake_case.
        """
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    async def fetch_and_save_movies_data(self, movie_title, limit=100):
        """
        Fetch and save movie data.

        Args:
            movie_title (str): The title of the movie to fetch.
            limit (int, optional): The maximum number of movies to fetch. Defaults to 100.
        """
        with UnitOfWork() as unit_of_work:
            repo = MoviesRepository(unit_of_work.session)
            parameters_global_search = self.config.get("parameters_global_search")
            parameters_global_search["s"] = movie_title
            movies_data = self.fetch_movies_data(
                self.config.get("url"),
                parameters_global_search,
                self.config.get("headers"),
                limit,
            )
            counter = 0
            if movies_data:
                loop = asyncio.get_event_loop()
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    logging.info(f"Fetching detailed movies data...")
                    for movie in movies_data:
                        if movie is not None:
                            imdb_id = movie.get("imdbID")
                            existing_movie = repo.get_by_id(imdb_id)
                            if not existing_movie:
                                tasks.append(
                                    loop.create_task(
                                        self.fetch_movie_data_by_imdb_id(
                                            self.config.get("url"),
                                            self.config.get("parameters_featch_by_id"),
                                            self.config.get("headers"),
                                            imdb_id,
                                        )
                                    )
                                )
                    logging.info(f"All request running, waiting for responses...")

                    for result in asyncio.as_completed(tasks):
                        movie_data = await result
                        if movie_data:
                            snake_case_movie = {
                                self.camel_to_snake(key): value
                                for key, value in movie_data.items()
                            }
                            if "response" in snake_case_movie:
                                del snake_case_movie["response"]
                            repo.add(MovieModel(**snake_case_movie))
                            logging.debug(f"Added: {snake_case_movie}")
                            counter += 1
                    repo.session.commit()
            logging.info(f"Saved {counter} new films.")


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.DEBUG)
        fetcher = MovieDataFetcher()
        with UnitOfWork() as unit_of_work:
            repo = MoviesRepository(unit_of_work.session)
            if repo.is_database_empty():  # Requires the database to be initilized
                asyncio.run(fetcher.fetch_and_save_movies_data("disney"))

    except HTTPError as e:
        logging.error(f"HTTPError: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError: {e}")
    except ValueError as e:
        logging.error(f"Error:", e)
    except Exception as e:
        logging.error(f"Error: {e}")
