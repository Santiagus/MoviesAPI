import json
import logging
from requests import Session
from requests.exceptions import HTTPError
from sqlalchemy import create_engine
from alembic.config import Config
from data_layer.unit_of_work import UnitOfWork
from data_layer.movies_repository import MoviesRepository
from data_layer.models import MovieModel, Base


def get_database_url_from_alembic_config():
    alembic_cfg = Config("alembic.ini")
    database_url = alembic_cfg.get_section_option("alembic", "sqlalchemy.url")
    if database_url is None:
        raise ValueError(
            "Database URL is missing or could not be retrieved from Alembic configuration"
        )
    return database_url


def fetch_movies_data(url, parameters, headers, limit=100):
    """
    Fetches movie data from the OMDB API and returns a list of movies.

    This function initializes a session, sends requests to the OMDB API to fetch movie data,
    and stores the data in a list. The function logs relevant information during the process.

    Args:
        url (str): The URL of the OMDB API.
        parameters (dict): The parameters for the API request.
        headers (dict): The headers for the API request.
        limit (int, optional): The maximum number of elements to preallocate in the list.
                              Defaults to 100.

    Returns:
        list: A list containing movie data fetched from the OMDB API.
    """
    logging.info("Data fetch started")

    # Set request config
    session = Session()

    # Preallocate memory
    movies_data_list = [None] * limit
    PAGE_SIZE = 10

    # Fetch movies data from specified url
    for page in range(10):
        parameters["page"] = page + 1
        response = session.get(url, headers=headers, params=parameters)
        logging.debug(f"Status code : {response.status_code}")
        logging.debug(f"Response : {response.text}")
        response.raise_for_status()  # Raise HTTPError if status code is not successful (>= 400)
        if response.status_code == 200:
            json_data = json.loads(response.text).get("Search")
            # Save to corresponding indexes int list
            start = page * PAGE_SIZE
            end = (page + 1) * PAGE_SIZE
            movies_data_list[start:end] = json_data[:PAGE_SIZE]
            if limit < end:  # Stops if limit passed
                break

    logging.info(f"Read {len(movies_data_list)} movies.")
    logging.info("Data fetch finished")
    return movies_data_list[:limit]


def fetch_movie_data_by_imdb_id(url, parameters, headers, imdb_id):
    logging.info("Data fetch started")
    parameters["i"] = imdb_id
    session = Session()
    response = session.get(url, headers=headers, params=parameters)

    logging.debug(f"Status code : {response.status_code}")
    logging.debug(f"Response : {response.text}")

    response.raise_for_status()  # Raise HTTPError if status code is not successful (>= 400)

    if response.status_code == 200:
        json_data = json.loads(response.text)
        logging.debug(f"Data: {json_data}")
        logging.info("Data fetch finished")
        return json_data


def camel_to_snake(name):
    """
    Convert camelCase string to snake_case.
    """
    import re

    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


if __name__ == "__main__":

    try:
        logging.basicConfig(level=logging.DEBUG)

        # Load config from JSON file
        with open("data_fetcher/fetcher_config.json", "r") as file:
            config = json.load(file)

        # Database Setup
        database_url = get_database_url_from_alembic_config()
        engine = create_engine(database_url)

        # Create all tables defined in the models
        Base.metadata.create_all(engine)

        # Fetch movies data with the specified config
        movies_data = fetch_movies_data(
            config.get("url"),
            config.get("parameters_global_search"),
            config.get("headers"),
            limit=1,
        )

        # Complete movie data and filter out None values
        logging.debug(f"Updating movies data...")
        movies_data = [
            fetch_movie_data_by_imdb_id(
                config.get("url"),
                config.get("parameters_featch_by_id"),
                config.get("headers"),
                movie.get("imdbID"),
            )
            for movie in movies_data
            if movie
        ]

        # Save into database
        with UnitOfWork() as unit_of_work:
            repo = MoviesRepository(unit_of_work.session)
            if repo.is_database_empty():
                logging.info("Empty Data Base. Collecting 100 movies sample.")
                for movie in movies_data:
                    if movie is not None:
                        snake_case_movie = {
                            camel_to_snake(key): value for key, value in movie.items()
                        }
                        repo.add(MovieModel(**snake_case_movie))
                repo.session.commit()
        logging.debug(f"Saved: \n {repo.get_all()}")
        logging.info("Program finished")

    except HTTPError as e:
        logging.error(f"HTTPError: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError: {e}")
    except ValueError as e:
        logging.error(f"Error:", e)
    except Exception as e:
        logging.error(f"Error: {e}")
