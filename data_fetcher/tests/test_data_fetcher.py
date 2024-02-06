import pytest
import json
from unittest.mock import patch, Mock, mock_open
from requests.exceptions import HTTPError, ConnectionError
from urllib3.exceptions import MaxRetryError, NameResolutionError
from data_fetcher.data_fetcher import fetch_movies_data


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

    # Patching the Session class and mocking the response
    with patch("data_fetcher.data_fetcher.Session") as mock_session:
        mock_session.return_value.get.return_value = mock_response
        # Calling the function
        result = fetch_movies_data(url, parameters, headers, 1)

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
    read_data='{"url": "https://example.com", "parameters": {"page": 1}, "headers": {"Accepts": "application/json"}}',
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
            config.get("url"), config.get("parameters"), config.get("headers")
        )
