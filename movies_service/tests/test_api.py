import pytest
from fastapi.testclient import TestClient
from movies_service.app import app
from movies_service.api import api
from unittest.mock import AsyncMock, MagicMock, patch
from starlette.exceptions import HTTPException


@pytest.fixture(scope="module")
def test_app():
    """Create a TestClient instance for testing the FastAPI app."""
    return TestClient(app)


def test_get_all_movies(test_app):
    movies_data = [
        {"Title": "Movie 1", "Year": "2000"},
        {"Title": "Movie 2", "Year": "2001"},
        {"Title": "Movie 3", "Year": "2002"},
    ]

    # Mocking the app.state.database_url
    test_app.app.state = MagicMock()
    test_app.app.state.database_url = "mocked_database_url"

    # Mocking the UnitOfWork class
    with patch("movies_service.api.api.UnitOfWork"), patch(
        "movies_service.api.api.MoviesRepository"
    ) as MockMoviesRepository:

        # mock_unit_of_work_instance = MockUnitOfWork.return_value
        mock_repo_instance = MockMoviesRepository.return_value

        # Set up the return value of is_database_empty and get_all methods
        mock_repo_instance.is_database_empty.return_value = False
        mock_repo_instance.get_all.return_value = movies_data

        # Make the request to the endpoint
        response = test_app.get("/movies")

        # Assert that the response is successful
        assert response.status_code == 200

        # Assert that the response body contains the expected movies data
        assert response.json() == movies_data


def test_get_all_movies_empty_database(test_app):
    # Mocking the app.state.database_url
    test_app.app.state = MagicMock()
    test_app.app.state.database_url = "mocked_database_url"

    # Mocking the UnitOfWork class
    with patch("movies_service.api.api.UnitOfWork"), patch(
        "movies_service.api.api.MoviesRepository"
    ) as MockMoviesRepository:

        # mock_unit_of_work_instance = MockUnitOfWork.return_value
        mock_repo_instance = MockMoviesRepository.return_value

        # Set up the return value of is_database_empty and get_all methods
        mock_repo_instance.is_database_empty.return_value = True

        # Make the request to the endpoint
        response = test_app.get("/movies")

        # Assert that the response is successful
        assert response.status_code == 404

        # Assert that the response body contains the expected movies data
        assert response.json() == {"detail": "Movies not found in the database"}


def test_get_movie_by_exact_title(test_app):
    movie_data = {"Title": "Movie 1", "Year": "2000"}

    # Mocking the app.state.database_url
    test_app.app.state = MagicMock()
    test_app.app.state.database_url = "mocked_database_url"

    # Mocking the UnitOfWork class
    with patch("movies_service.api.api.UnitOfWork"), patch(
        "movies_service.api.api.MoviesRepository"
    ) as MockMoviesRepository:

        # mock_unit_of_work_instance = MockUnitOfWork.return_value
        mock_repo_instance = MockMoviesRepository.return_value

        # Set up the return value of is_database_empty and get_all methods
        mock_repo_instance.is_database_empty.return_value = False
        mock_repo_instance.get_by_title.return_value = movie_data

        # Make the request to the endpoint
        response = test_app.get("/movie/title_to_search")

        # Assert that the response is successful
        assert response.status_code == 200

        # Assert that the response body contains the expected movies data
        assert response.json() == movie_data


def test_get_movie_by_mismatching_title(test_app):
    # Mocking the app.state.database_url
    test_app.app.state = MagicMock()
    test_app.app.state.database_url = "mocked_database_url"

    # Mocking the UnitOfWork class
    with patch("movies_service.api.api.UnitOfWork"), patch(
        "movies_service.api.api.MoviesRepository"
    ) as MockMoviesRepository:

        # mock_unit_of_work_instance = MockUnitOfWork.return_value
        mock_repo_instance = MockMoviesRepository.return_value

        # Set up the return value of is_database_empty and get_all methods
        mock_repo_instance.is_database_empty.return_value = False
        mock_repo_instance.get_by_title.return_value = dict()

        # Make the request to the endpoint
        response = test_app.get("/movie/title_to_search")

        # Assert that the response is successful
        assert response.status_code == 404

        # Assert that the response body contains the expected movies data
        assert response.json() == {
            "detail": 'No exact match for "title_to_search" in the database.'
        }


def test_get_movie_in_empty_database(test_app):
    # Mocking the app.state.database_url
    test_app.app.state = MagicMock()
    test_app.app.state.database_url = "mocked_database_url"

    # Mocking the UnitOfWork class
    with patch("movies_service.api.api.UnitOfWork"), patch(
        "movies_service.api.api.MoviesRepository"
    ) as MockMoviesRepository:

        # mock_unit_of_work_instance = MockUnitOfWork.return_value
        mock_repo_instance = MockMoviesRepository.return_value

        # Set up the return value of is_database_empty and get_all methods
        mock_repo_instance.is_database_empty.return_value = True
        # mock_repo_instance.get_by_title.return_value = dict()

        # Make the request to the endpoint
        response = test_app.get("/movie/title_to_search")

        # Assert that the response is successful
        assert response.status_code == 404

        # Assert that the response body contains the expected movies data
        assert response.json() == {"detail": "Movie not found in the database"}


def test_post_movie_by_title(test_app):
    movies_titles = ["Title 1"]
    # Mocking the fetch_and_save_movies_data method
    test_app.app.state.mdf = AsyncMock()
    test_app.app.state.mdf.fetch_and_save_movies_data.return_value = movies_titles

    # Make the request to the endpoint
    response = test_app.post("/movie/title_to_search")

    # Assert that the response is successful
    assert response.status_code == 200

    # Assert that the response body contains the expected movies data
    assert response.json() == {"Saved": movies_titles}


def test_post_movie_by_title_no_match(test_app):
    movies_titles = []
    # Mocking the fetch_and_save_movies_data method
    test_app.app.state.mdf = AsyncMock()
    test_app.app.state.mdf.fetch_and_save_movies_data.return_value = movies_titles

    # Make the request to the endpoint
    response = test_app.post("/movie/title_to_search")

    # Assert that the response is successful
    assert response.status_code == 200

    # Assert that the response body contains the expected movies data
    assert response.json() == {"Saved": movies_titles}


@patch("movies_service.api.api.is_api_key_valid", return_value=True)
def test_delete_movie_by_imdb_id_with_valid_api_key(mock_api_verification, test_app):
    # Mocking the app.state.database_url
    test_app.app.state = MagicMock()
    test_app.app.state.database_url = "mocked_database_url"

    # Mocking the UnitOfWork class
    with patch("movies_service.api.api.UnitOfWork"), patch(
        "movies_service.api.api.MoviesRepository"
    ) as MockMoviesRepository:

        # mock_unit_of_work_instance = MockUnitOfWork.return_value
        mock_repo_instance = MockMoviesRepository.return_value

        # Set up the return value of is_database_empty and get_all methods
        mock_repo_instance.is_database_empty.return_value = False
        mock_repo_instance.delete_by_id.return_value = True

        # Make the request to the endpoint
        response = test_app.delete("/movie/imdb_to_search")

        # Assert that the response is successful
        assert response.status_code == 200

        # Assert that the response body contains the expected movies data
        assert response.json() == {
            "detail": f"Movie with ID imdb_to_search was deleted successfully"
        }


@patch("movies_service.api.api.is_api_key_valid", return_value=True)
def test_delete_movie_not_in_database_imdb_id_with_valid_api_key(
    mock_api_verification, test_app
):
    # Mocking the app.state.database_url
    test_app.app.state = MagicMock()
    test_app.app.state.database_url = "mocked_database_url"

    # Mocking the UnitOfWork class
    with patch("movies_service.api.api.UnitOfWork"), patch(
        "movies_service.api.api.MoviesRepository"
    ) as MockMoviesRepository:

        # mock_unit_of_work_instance = MockUnitOfWork.return_value
        mock_repo_instance = MockMoviesRepository.return_value

        # Set up the return value of is_database_empty and get_all methods
        mock_repo_instance.is_database_empty.return_value = False
        mock_repo_instance.delete_by_id.return_value = False

        # Make the request to the endpoint
        response = test_app.delete("/movie/imdb_to_search")

        # Assert that the response is successful
        assert response.status_code == 404

        # Assert that the response body contains the expected movies data
        assert response.json() == {"detail": f"Movie not found in the database"}


@patch("movies_service.api.api.is_api_key_valid", return_value=False)
def test_delete_movie_by_imdb_id_with_invalid_api_key(mock_api_verification, test_app):
    # Make the request to the endpoint
    response = test_app.delete("/movie/imdb_to_search")

    # Assert that the response is successful
    assert response.status_code == 401

    # Assert that the response body contains the expected movies data
    assert response.json() == {"detail": "Invalid API key"}


def test_is_api_key_valid():
    # Valid API key
    response = api.is_api_key_valid("Movies_API_KEY_number_1")
    assert response == True


def test_is_api_key_invalid():
    # Invalid API key
    response = api.is_api_key_valid("Invalid_API_key")
    assert response == False
