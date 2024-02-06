import json
import logging
from requests import Session
from requests.exceptions import HTTPError


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

    logging.info(f"Read {len(movies_data_list)} movies.")
    logging.info("Data fetch finished")
    return movies_data_list[:limit]


if __name__ == "__main__":

    try:
        logging.basicConfig(level=logging.INFO)

        # Load config from JSON file
        with open("data_fetcher/fetcher_config.json", "r") as file:
            config = json.load(file)

        # Fetch movies data with the specified config
        movies_data = fetch_movies_data(
            config.get("url"), config.get("parameters"), config.get("headers")
        )
        logging.info("Program finished")

    except HTTPError as e:
        logging.error(f"HTTPError: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")
