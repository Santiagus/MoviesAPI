import pytest
import json
from unittest.mock import patch, Mock, mock_open
from requests.exceptions import HTTPError, ConnectionError
from urllib3.exceptions import MaxRetryError, NameResolutionError
from data_fetcher.data_fetcher import fetch_movies_data, fetch_movie_data_by_imdb_id


def test_fetch_movies_data_success():
    """
    Test the fetch_movies_data function with a successful response.

    The function should correctly handle a successful response from the OMDB API
    and return the expected movie data.

    Returns:
        None
    """
    # Test setup
    url = "https://example.com"
    parameters = {"page": 1}
    headers = {"Accepts": "application/json"}

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"Search": [{"Title": "Movie 1"}]}'
    limit = 1
    # Patching the Session class and mocking the response
    with patch("data_fetcher.data_fetcher.Session") as mock_session:
        mock_session.return_value.get.return_value = mock_response
        # Calling the function
        result = fetch_movies_data(url, parameters, headers, limit)

    # Assertion
    assert result == [{"Title": "Movie 1"}]


def test_fetch_movies_data_http_error():
    """
    Test the fetch_movies_data function with an HTTP error response.

    The function should raise an HTTPError when encountering an error response
    from the OMDB API.

    Returns:
        None
    """
    # Test setup
    url = "https://example.com"
    parameters = {"page": 1}
    headers = {"Accepts": "application/json"}

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError()

    # Patching the Session class and mocking the response
    with patch("data_fetcher.data_fetcher.Session") as mock_session:
        mock_session.return_value.get.return_value = mock_response

        # Assertion for expected HTTPError
        with pytest.raises(HTTPError):
            fetch_movies_data(url, parameters, headers)


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"url": "https://example.com", "parameters_global_search": {"page": 1}, "headers": {"Accepts": "application/json"}}',
)
@patch(
    "data_fetcher.data_fetcher.fetch_movies_data",
    side_effect=[ConnectionError, MaxRetryError, NameResolutionError],
)
def test_fetch_movies_with_config_connection_error(mock_fetch_movies_data, mock_open):
    # Arrange
    # No need to mock fetch_movies_data as we're testing HTTPError handling

    # Act & Assert
    with pytest.raises(ConnectionError):
        with open("data_fetcher/fetcher_config.json", "r") as file:
            config = json.load(file)
        fetch_movies_data(
            config.get("url"),
            config.get("parameters_global_search"),
            config.get("headers"),
        )


def test_fetch_movie_data_by_imdb_id_success():
    """
    Test the fetch_movies_data function with a successful response.

    The function should correctly handle a successful response from the OMDB API
    and return the expected movie data.

    Returns:
        None
    """
    # Test setup
    movie_data = {
        "title": "Ultimate Fan's Guide to Walt Disney World",
        "year": "2004",
        "rated": "N/A",
        "released": "N/A",
        "runtime": "56 min",
        "genre": "N/A",
        "director": "N/A",
        "writer": "Jamie Iracleanos",
        "actors": "David Lloyd, Bethany Lloyd, Stephen Lloyd",
        "plot": "Follow four groups of fans as they share their tips on the best ways to visit the Walt Disney World Resort. A family with young children, another family with teenagers, a newlywed couple, and finally a group of young adult friends share with you their secrets for a successful vacation!",
        "language": "English",
        "country": "United States",
        "awards": "N/A",
        "poster": "https://m.media-amazon.com/images/M/MV5BMTQyMzY5Mjg5NV5BMl5BanBnXkFtZTgwMzI5OTk1MDE@._V1_SX300.jpg",
        "ratings": [{"Source": "Internet Movie Database", "Value": "8.6/10"}],
        "metascore": "N/A",
        "imdb_rating": "8.6",
        "imdb_votes": "32",
        "imdb_id": "tt0362300",
        "type": "movie",
        "dvd": "N/A",
        "box_office": "N/A",
        "production": "N/A",
        "website": "N/A",
        "response": "True",
    }

    url = "https://example.com"
    parameters = {"page": 1}
    headers = {"Accepts": "application/json"}
    imdb_id = movie_data["imdb_id"]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps(movie_data)

    # Patching the Session class and mocking the response
    with patch("data_fetcher.data_fetcher.Session") as mock_session:
        mock_session.return_value.get.return_value = mock_response
        # Calling the function
        result = fetch_movie_data_by_imdb_id(url, parameters, headers, imdb_id)

    # Assertion
    assert result == movie_data


def test_fetch_movie_data_by_imdb_id_http_error():
    """
    Test the fetch_movies_data function with an HTTP error response.

    The function should raise an HTTPError when encountering an error response
    from the OMDB API.

    Returns:
        None
    """
    # Test setup
    url = "https://example.com"
    parameters = {"page": 1}
    headers = {"Accepts": "application/json"}
    imdb_id = "tt0362300"

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError()

    # Patching the Session class and mocking the response
    with patch("data_fetcher.data_fetcher.Session") as mock_session:
        mock_session.return_value.get.return_value = mock_response

        # Assertion for expected HTTPError
        with pytest.raises(HTTPError):
            fetch_movie_data_by_imdb_id(url, parameters, headers, imdb_id)


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"url": "https://example.com", "parameters_featch_by_id": {"page": 1}, "headers": {"Accepts": "application/json"}}',
)
@patch(
    "data_fetcher.data_fetcher.fetch_movies_data",
    side_effect=[ConnectionError, MaxRetryError, NameResolutionError],
)
def test_fetch_movie_data_by_imdb_id_with_config_connection_error(
    mock_fetch_movies_data, mock_open
):
    # Arrange
    # No need to mock fetch_movies_data as we're testing HTTPError handling

    # Act & Assert
    with pytest.raises(ConnectionError):
        with open("data_fetcher/fetcher_config.json", "r") as file:
            config = json.load(file)
        fetch_movie_data_by_imdb_id(
            config.get("url"),
            config.get("parameters_featch_by_id"),
            config.get("headers"),
            config.get("headers"),
        )
