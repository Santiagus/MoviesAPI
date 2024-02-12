import pytest
from fastapi.testclient import TestClient
from movies_service.app import app
from unittest.mock import MagicMock, patch


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
    title_to_search = "Movie 1"
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
        response = test_app.get("/movie/{title_to_search}")

        # Assert that the response is successful
        assert response.status_code == 200

        # Assert that the response body contains the expected movies data
        assert response.json() == movie_data
