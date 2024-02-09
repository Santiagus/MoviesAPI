import aiohttp
import asyncio

import logging

from requests.exceptions import HTTPError
from sqlalchemy import create_engine
from data_layer.unit_of_work import UnitOfWork
from data_layer.movies_repository import MoviesRepository
from data_layer.models import MovieModel, Base
from common import utils


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
        self.config = utils.load_config(config_file_path)
        self.database_url = utils.get_database_url_from_alembic_config(alembic_config)
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)

    @staticmethod
    async def fetch_page(session, url, parameters, headers, page=1):
        """
        Fetch a page of movie data from the OMDB API.

        Args:
            session (aiohttp.ClientSession): The aiohttp session for making HTTP requests.
            url (str): The URL of the OMDB API.
            parameters (dict): The parameters for the API request.
            headers (dict): The headers for the API request.
            page (int, optional): The page number to fetch. Defaults to 1.

        Returns:
            dict: The JSON response containing movie data from the specified page.
        """
        logging.info(f"Fetching Page: {page: <4}")
        parameters["page"] = page
        response = await session.get(url, headers=headers, params=parameters)
        return await response.json()

    @staticmethod
    async def fetch_movies_data(session, url, parameters, headers, limit=100):
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
        logging.info(f"Data fetch started with search param : {parameters.get('s')}")

        PAGE_SIZE = 10
        movies_data_list = [None] * limit

        # First request
        response = await MovieDataFetcher.fetch_page(session, url, parameters, headers)

        if response.get("Response") != "True":
            raise Exception(f"Error: {response.get('Error')}")

        total_results = int(response.get("totalResults", 0))

        # Check data in response
        if total_results == 0:
            logging.warning("No results found.")
            return []

        # Save movies data
        movies_data = response.get("Search", [])
        received_movies_data = len(movies_data)
        movies_data_list[0:received_movies_data] = movies_data[:received_movies_data]

        # Calculate remaining request needed to gather all needed movies data
        remaining_results = max(limit - PAGE_SIZE, 0)
        remaining_requests = (remaining_results // PAGE_SIZE) + min(
            1, remaining_results % PAGE_SIZE
        )

        # Fetch remaining request concurrently
        tasks = []
        page = 1
        for _ in range(remaining_requests):
            page += 1
            parameters["page"] = page
            tasks.append(
                MovieDataFetcher.fetch_page(session, url, parameters, headers, page)
            )

        additional_movies_data = await asyncio.gather(*tasks)

        # Save remaining data
        idx = received_movies_data
        for response in additional_movies_data:
            movies_data = response.get("Search", [])
            if movies_data:
                movies_data_list[idx : idx + len(movies_data)] = movies_data
                idx += len(movies_data)

        logging.info(f"Read {len(movies_data_list)} movies.")
        return movies_data_list[:idx]

    @staticmethod
    async def fetch_movie_data_by_imdb_id(session, url, parameters, headers, imdb_id):
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
        response = await session.get(url, headers=headers, params=parameters)
        response_json = await response.json()

        logging.debug(f"Status code : {response.status}")
        logging.debug(f"Response : {response_json}")

        if response.status == 200:
            return response_json
        return {}

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
        with UnitOfWork(self.database_url) as unit_of_work:
            repo = MoviesRepository(unit_of_work.session)
            parameters_global_search = self.config.get("parameters_global_search")
            parameters_global_search["s"] = movie_title
            async with aiohttp.ClientSession() as session:
                movies_data = await self.fetch_movies_data(
                    session,
                    self.config.get("url"),
                    parameters_global_search,
                    self.config.get("headers"),
                    limit,
                )
                counter = 0
                if movies_data:
                    loop = asyncio.get_event_loop()
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
                                            session,
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
        logging.basicConfig(level=logging.INFO)
        fetcher = MovieDataFetcher()
        database_url = utils.get_database_url_from_alembic_config()
        with UnitOfWork(database_url) as unit_of_work:
            repo = MoviesRepository(unit_of_work.session)
            if repo.is_database_empty():  # Requires the database to be initilized
                asyncio.run(fetcher.fetch_and_save_movies_data("disney"))
            else:
                logging.info("Database is not empty. Program terminated")
    except HTTPError as e:
        logging.error(f"HTTPError: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError: {e}")
    except ValueError as e:
        logging.error(f"Error:", e)
    except Exception as e:
        logging.error(f"Error: {e}")
