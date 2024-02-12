from urllib import response
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from sqlalchemy import false
from data_fetcher.movie_data_fetcher import MovieDataFetcher


@pytest.mark.asyncio
async def test_fetch_page():
    url = "https://example.com"
    parameters = {"param1": "value1", "param2": "value2"}
    headers = {"header1": "value1", "header2": "value2"}
    page = 2

    # Mock the response of the session.get method
    response_data = {
        "Search": [
            {
                "Title": "I Killed My Lesbian Wife, Hung Her on a Meathook, and Now I Have a Three Picture Deal at Disney",
                "Year": "1993",
                "imdbID": "tt0166222",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BOTNlZDMxMDItM2M4Yy00NDNkLWJkOTMtMTJkMTRlYTNiZjNkXkEyXkFqcGdeQXVyNjMxODMyODU@._V1_SX300.jpg",
            },
            {
                "Title": "Walt Disney Animation Studios Short Films Collection",
                "Year": "2015",
                "imdbID": "tt6181728",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BYTdkYjkyMzgtMjQyOC00ZmNiLTg1OTAtNzJhY2MyNjlmM2M5XkEyXkFqcGdeQXVyNDgyODgxNjE@._V1_SX300.jpg",
            },
            {
                "Title": "The Story of Frozen: Making a Disney Animated Classic",
                "Year": "2014",
                "imdbID": "tt4007494",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BMTk0NjAzNjg4NF5BMl5BanBnXkFtZTgwNDQ3NjIwMzE@._V1_SX300.jpg",
            },
            {
                "Title": "One Day at Disney",
                "Year": "2019",
                "imdbID": "tt11550148",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BNzhiZDk5ZDUtY2E1MS00YzRlLWI2NjYtZWYyNzNjNTkyZjE4XkEyXkFqcGdeQXVyMTE5NDQ1MzQ3._V1_SX300.jpg",
            },
            {
                "Title": "LEGO Disney Princess: The Castle Quest",
                "Year": "2023",
                "imdbID": "tt28477869",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BMWQ0MjJjZjUtNmU1Zi00ODc3LWE5ZWMtMjIyM2QxMDA0NGZjXkEyXkFqcGdeQXVyMTM1NjM2ODg1._V1_SX300.jpg",
            },
            {
                "Title": "Disney Princess Enchanted Tales: Follow Your Dreams",
                "Year": "2007",
                "imdbID": "tt1135924",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BNDRlMWI1NTYtNDA0ZS00ZDcyLTg5NDQtOTQ4NTE5NjAxNzg1XkEyXkFqcGdeQXVyNDgyODgxNjE@._V1_SX300.jpg",
            },
            {
                "Title": "The Disney Family Singalong",
                "Year": "2020",
                "imdbID": "tt12131604",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BNjQ2MDA2ZDUtZGJhZi00N2FjLWIyNjAtODFkOTkwNDRiYmRhXkEyXkFqcGdeQXVyMTAwMzM3NDI3._V1_SX300.jpg",
            },
            {
                "Title": "The Muppets at Walt Disney World",
                "Year": "1990",
                "imdbID": "tt0244084",
                "Type": "movie",
                "Poster": "N/A",
            },
            {
                "Title": "A Walt Disney Christmas",
                "Year": "1982",
                "imdbID": "tt0483445",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BZTQyODYzMTEtMjE3YS00NzUyLTg0YTItOTE4OTU4ZjIzMDdhXkEyXkFqcGdeQXVyMzU0NzkwMDg@._V1_SX300.jpg",
            },
            {
                "Title": "Disney Sing-Along-Songs: Disneyland Fun",
                "Year": "1990",
                "imdbID": "tt0284050",
                "Type": "movie",
                "Poster": "https://m.media-amazon.com/images/M/MV5BMTM1NDQ5MDk3NF5BMl5BanBnXkFtZTcwNzk2MjAzMQ@@._V1_SX300.jpg",
            },
        ],
        "totalResults": "499",
        "Response": "True",
    }
    session_mock = AsyncMock()

    # Create a response object with the required attributes
    response_mock = AsyncMock()
    response_mock.json = AsyncMock(return_value=response_data)

    # Set the return_value of session.get to return the response object
    session_mock.get.return_value = response_mock

    # Call the function under test
    result = await MovieDataFetcher.fetch_page(
        session_mock, url, parameters, headers, page
    )

    # Assertions
    assert result == response_data
    session_mock.get.assert_awaited_once_with(url, headers=headers, params=parameters)
    response_mock.json.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_movies_data_successful_request():
    # Define test data
    url = "http://www.omdbapi.com/"
    parameters = {"apikey": "test_api_key", "s": "test_query"}
    headers = {"Accepts": "application/json"}
    limit = 10

    # Set up mock response data
    response_data = {
        "Search": [
            {"Title": "Movie 1", "Year": "2000"},
            {"Title": "Movie 2", "Year": "2001"},
        ],
        "totalResults": "2",
        "Response": "True",
    }

    # Create a response object with the required attributes
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = response_data

    # Set the return_value of session.get to return the response object
    session_mock = AsyncMock()
    session_mock.get.return_value = mock_response

    # Call the method under test
    movies_data = await MovieDataFetcher.fetch_movies_data(
        session_mock, url, parameters, headers, limit
    )

    # Assertions
    assert len(movies_data) == 2
    assert movies_data[0]["Title"] == "Movie 1"
    assert movies_data[1]["Title"] == "Movie 2"


@pytest.mark.asyncio
async def test_fetch_movies_data_successful_multi_request():
    # Define test data
    url = "http://www.omdbapi.com/"
    parameters = {"apikey": "test_api_key", "s": "test_query"}
    headers = {"Accepts": "application/json"}
    limit = 20

    # Set up mock response data
    response_data = {
        "Search": [
            {"Title": "Movie 1", "Year": "2000"},
            {"Title": "Movie 2", "Year": "2001"},
        ],
        "totalResults": "15",
        "Response": "True",
    }

    # Create a response object with the required attributes
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = response_data

    # Set the return_value of session.get to return the response object
    session_mock = AsyncMock()
    session_mock.get.return_value = mock_response

    # Call the method under test
    movies_data = await MovieDataFetcher.fetch_movies_data(
        session_mock, url, parameters, headers, limit
    )

    # Assertions
    assert movies_data != None
    assert len(movies_data) == 4
    assert movies_data[0]["Title"] == "Movie 1"
    assert movies_data[1]["Title"] == "Movie 2"
    assert movies_data[2]["Title"] == "Movie 1"
    assert movies_data[3]["Title"] == "Movie 2"


@pytest.mark.asyncio
async def test_fetch_movies_data_response_false():
    # Define test data
    url = "http://www.omdbapi.com/"
    parameters = {"apikey": "test_api_key", "s": "test_query"}
    headers = {"Accepts": "application/json"}
    limit = 10

    response_data = {"Response": "False"}
    with patch(
        "data_fetcher.movie_data_fetcher.MovieDataFetcher.fetch_page",
        return_value=response_data,
    ):
        session_mock = MagicMock()

        # Call the method under test
        with pytest.raises(Exception):
            await MovieDataFetcher.fetch_movies_data(
                session_mock, url, parameters, headers, limit
            )


@pytest.mark.asyncio
async def test_fetch_movies_data_no_results():
    # Define test data
    url = "http://www.omdbapi.com/"
    parameters = {"apikey": "test_api_key", "s": "test_query"}
    headers = {"Accepts": "application/json"}
    limit = 10

    response_data = {"Response": "True", "totalResults": 0}
    with patch(
        "data_fetcher.movie_data_fetcher.MovieDataFetcher.fetch_page",
        return_value=response_data,
    ):
        session_mock = MagicMock()

        # Call the method under test
        response = await MovieDataFetcher.fetch_movies_data(
            session_mock, url, parameters, headers, limit
        )
        assert response == []


@pytest.mark.asyncio
async def test_fetch_movies_data_api_key_error():
    # Define test data
    url = "http://www.omdbapi.com/"
    parameters = {"apikey": "test_api_key", "s": "non_existant_movie"}
    headers = {"Accepts": "application/json"}
    limit = 10

    # Set up mock response data with error
    response_data = {"Response": "False", "Error": "Invalid API key!"}
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response = response_data

    # Set the return_value of session.get to return the response object
    session_mock = AsyncMock()
    session_mock.get.return_value = mock_response

    # Call the method under test and expect an exception
    with pytest.raises(Exception) as exc_info:
        await MovieDataFetcher.fetch_movies_data(
            session_mock, url, parameters, headers, limit
        )

        # Assertion
        assert str(exc_info.value) == "Error: Invalid API key!"


@pytest.mark.asyncio
async def test_fetch_movie_data_by_imdb_id():
    # Define test data
    url = "https://example.com"
    parameters = {"i": "tt0362300", "page": 1}
    headers = {"Accepts": "application/json"}
    imdb_id = "tt0362300"

    # Example response data
    response_data = {
        "Title": "Inception",
        "Year": "2010",
        "imdbID": "tt1375666",
    }

    # Create a response object with the required attributes
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = response_data

    # Set the return_value of session.get to return the response object
    session_mock = AsyncMock()
    session_mock.get.return_value = mock_response

    # Call the function under test
    result = await MovieDataFetcher.fetch_movie_data_by_imdb_id(
        session_mock, url, parameters, headers, imdb_id
    )

    # Assertions
    assert result == response_data
    session_mock.get.assert_awaited_once_with(url, headers=headers, params=parameters)
    mock_response.json.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_movie_data_by_imdb_id_no_results_found():
    # Define test data
    url = "https://example.com"
    parameters = {"i": "tt0362300", "page": 1}
    headers = {"Accepts": "application/json"}
    imdb_id = "tt0362300"

    # Example response data
    response_data = {}

    # Create a response object with the required attributes
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.json.return_value = response_data

    # Set the return_value of session.get to return the response object
    session_mock = AsyncMock()
    session_mock.get.return_value = mock_response

    # Call the function under test
    result = await MovieDataFetcher.fetch_movie_data_by_imdb_id(
        session_mock, url, parameters, headers, imdb_id
    )

    # Assertions
    assert result == response_data
    session_mock.get.assert_awaited_once_with(url, headers=headers, params=parameters)
    mock_response.json.assert_awaited_once()


def test_camel_to_snake():
    # Test cases
    test_cases = [
        ("camelCase", "camel_case"),
        ("someVariable", "some_variable"),
        ("AnotherExample", "another_example"),
        ("HTMLDocument", "html_document"),
        ("myAPIEndpoint", "my_api_endpoint"),
        ("UserID", "user_id"),
    ]

    # Iterate over test cases
    for input_str, expected_output in test_cases:
        # Call the method under test
        result = MovieDataFetcher.camel_to_snake(input_str)

        # Assert the result
        assert (
            result == expected_output
        ), f"Expected {expected_output}, but got {result}"


class session:
    def commit(self):
        return None


class MockMoviesRepoFixture:

    def __init__(self):
        self.movie_instances = []
        self.session = session()
        self.add_counter = 0

    # Mock the behavior of the add method to append MovieModel instances to the list
    def add(self, movie):
        self.movie_instances.append(movie)
        self.add_counter += 1
        print("MockMoviesRepoFixture add_counter :", self.add_counter)

    # Mock the behavior of the get_all method to return the list of MovieModel instances
    def get_all(self, limit=100):
        return [movie.to_dict() for movie in self.movie_instances[:limit]]

    # Mock the behavior of the get_by_id method to return a MovieModel from the list if there is a match
    def get_by_id(self, imdb_id):
        for movie in self.movie_instances:
            if movie.imdb_id == imdb_id:
                return movie
        return None

    # Mock the behavior of the get_by_title method to return a MovieModel from the list if there is a match
    def get_by_title(self, title):
        for movie in self.movie_instances:
            if movie.title == title:
                return movie
        return None

    # Mock the behavior of the get_delete_by_id method to return a MovieModel from the list if there is a match
    def delete_by_id(self, imdb_id):
        for movie in self.movie_instances:
            if movie.imdb_id == imdb_id:
                del movie
                return True, "Movie deleted successfully"
        return False, "Movie not found"


def test_fetch_and_save_movies_data():
    # Set up mock config
    fetcher = MovieDataFetcher()
    fetcher.config = {
        "url": "https://example.com",
        "parameters_global_search": {"s": "Movie Title"},
        "parameters_featch_by_id": {"i": "imdb_id"},
        "headers": {"Accepts": "application/json"},
    }

    # Call the method under test
    with patch(
        "data_fetcher.movie_data_fetcher.MovieDataFetcher.fetch_movie_data_by_imdb_id"
    ) as mock_fetch_movies_data_by_id:
        movie_data = {
            "Title": "Ultimate Fan's Guide to Walt Disney World",
            "Year": "2004",
            "Runtime": "56 min",
            "imdbID": "tt1234567",
        }
        mock_fetch_movies_data_by_id.return_value = movie_data
        with patch(
            "data_fetcher.movie_data_fetcher.MovieDataFetcher.fetch_movies_data"
        ) as mock_fetch_movies_data:
            movies_data = [
                {
                    "imdbID": "tt1234567",
                    "Title": "Ultimate Fan's Guide to Walt Disney World",
                }
            ]

            mock_fetch_movies_data.return_value = movies_data
            with patch(
                "data_fetcher.movie_data_fetcher.MoviesRepository"
            ) as mock_movies_repo:
                mock_movies_repo.return_value = MockMoviesRepoFixture()
                with patch(
                    "data_fetcher.movie_data_fetcher.aiohttp.ClientSession"
                ) as session:
                    session.return_value = AsyncMock()
                    with patch("data_fetcher.movie_data_fetcher.UnitOfWork") as uow:
                        # Define what uow returns
                        mock_unit_of_work = MagicMock()
                        mock_unit_of_work.session = MagicMock()
                        uow.return_value = mock_unit_of_work

                        asyncio.run(
                            fetcher.fetch_and_save_movies_data("Movie Title", limit=100)
                        )

                        # Assert that the session was created and used
                        session.assert_called_once()
                        uow.assert_called_once()

                        # Assert that fetch_movies_data was called with the correct arguments
                        mock_fetch_movies_data.assert_called_once()

                        saved_movies = mock_movies_repo.return_value.get_all()
                        # Transform keys to snake case
                        movie_data = {
                            "Title": "Ultimate Fan's Guide to Walt Disney World",
                            "Year": "2004",
                            "Runtime": "56 min",
                            "imdbID": "tt1234567",
                        }
                        assert movie_data.get("Title") == saved_movies[0].get("Title")
                        assert movie_data.get("year") == saved_movies[0].get("year")
                        assert movie_data.get("Runtime") == saved_movies[0].get(
                            "Runtime"
                        )
                        assert movie_data.get("imdbID") == saved_movies[0].get("imdbID")


def test_fetch_and_save_movies_data_filter_response_key():
    # Set up mock config
    fetcher = MovieDataFetcher()
    fetcher.config = {
        "url": "https://example.com",
        "parameters_global_search": {"s": "Movie Title"},
        "parameters_featch_by_id": {"i": "imdb_id"},
        "headers": {"Accepts": "application/json"},
    }

    # Call the method under test
    with patch(
        "data_fetcher.movie_data_fetcher.MovieDataFetcher.fetch_movie_data_by_imdb_id"
    ) as mock_fetch_movies_data_by_id:
        movie_data = {
            "Title": "Ultimate Fan's Guide to Walt Disney World",
            "Year": "2004",
            "Runtime": "56 min",
            "imdbID": "tt1234567",
            "Response": "True",
        }
        mock_fetch_movies_data_by_id.return_value = movie_data
        with patch(
            "data_fetcher.movie_data_fetcher.MovieDataFetcher.fetch_movies_data"
        ) as mock_fetch_movies_data:
            movies_data = [
                {
                    "imdbID": "tt1234567",
                    "Title": "Ultimate Fan's Guide to Walt Disney World",
                }
            ]

            mock_fetch_movies_data.return_value = movies_data
            with patch(
                "data_fetcher.movie_data_fetcher.MoviesRepository"
            ) as mock_movies_repo:
                mock_movies_repo.return_value = MockMoviesRepoFixture()
                with patch(
                    "data_fetcher.movie_data_fetcher.aiohttp.ClientSession"
                ) as session:
                    session.return_value = AsyncMock()
                    with patch("data_fetcher.movie_data_fetcher.UnitOfWork") as uow:
                        # Define what uow returns
                        mock_unit_of_work = MagicMock()
                        mock_unit_of_work.session = MagicMock()
                        uow.return_value = mock_unit_of_work

                        asyncio.run(
                            fetcher.fetch_and_save_movies_data("Movie Title", limit=100)
                        )

                        # Assert that the session was created and used
                        session.assert_called_once()
                        uow.assert_called_once()

                        # Assert that fetch_movies_data was called with the correct arguments
                        mock_fetch_movies_data.assert_called_once()

                        saved_movies = mock_movies_repo.return_value.get_all()
                        # Transform keys to snake case
                        movie_data = {
                            "Title": "Ultimate Fan's Guide to Walt Disney World",
                            "Year": "2004",
                            "Runtime": "56 min",
                            "imdbID": "tt1234567",
                        }
                        assert movie_data.get("Title") == saved_movies[0].get("Title")
                        assert movie_data.get("year") == saved_movies[0].get("year")
                        assert movie_data.get("Runtime") == saved_movies[0].get(
                            "Runtime"
                        )
                        assert movie_data.get("imdbID") == saved_movies[0].get("imdbID")
