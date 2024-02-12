from h11 import Data
from httpx import delete
import pytest
from unittest.mock import Mock, MagicMock
from data_layer.models import MovieModel
from data_layer.movies_repository import MoviesRepository
from sqlalchemy.exc import OperationalError, DatabaseError


@pytest.fixture
def mock_session():
    return Mock()


def test_add_movie(mock_session):
    # Create a movie instance
    movie = MovieModel(
        imdb_id="tt1375666", title="Inception", year=2010, director="Christopher Nolan"
    )

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)
    movies_repo.add(movie)

    # Assert that the session's add method is called with the movie instance
    mock_session.add.assert_called_once_with(movie)


def test_get_movie_by_id(mock_session):
    # Mocking the query method of the session
    mock_session.query().filter().one_or_none.return_value = MovieModel(
        imdb_id="tt1375666",
        title="Inception",
        year="2010",
        director="Christopher Nolan",
    )

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the get_by_id method
    movie = movies_repo.get_by_id("tt1375666")

    assert movie != dict()
    # Assert that the returned movie has the correct attributes
    if movie:
        assert movie.get("Title") == "Inception"
        assert movie.get("Year") == "2010"
        assert movie.get("Director") == "Christopher Nolan"


def test_get_movie_by_id_no_match(mock_session):
    # Mocking the query method of the session
    mock_session.query().filter().one_or_none.return_value = None

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the get_by_id method
    movie = movies_repo.get_by_id("tt1375666")

    assert movie == None


def test_get_movie_by_title(mock_session):
    # Mocking the query method of the session
    mock_session.query().filter().one_or_none.return_value = MovieModel(
        imdb_id="tt1375666",
        title="Inception",
        year="2010",
        director="Christopher Nolan",
    )

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the get_by_id method
    movie = movies_repo.get_by_title("Inception")

    assert movie != dict()
    # Assert that the returned movie has the correct attributes
    if movie:
        assert movie.get("imdbID") == "tt1375666"
        assert movie.get("Title") == "Inception"
        assert movie.get("Year") == "2010"
        assert movie.get("Director") == "Christopher Nolan"


def test_get_movie_by_title_no_match(mock_session):
    # Mocking the query method of the session
    mock_session.query().filter().one_or_none.return_value = None

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the get_by_id method
    movie = movies_repo.get_by_title("no_match_title")

    assert movie == None


def test_delete_movie_by_id(mock_session):
    # Mocking the query method of the session
    mock_session.query().filter_by().first.return_value = MovieModel(
        imdb_id="tt1375666", title="Inception", year=2010, director="Christopher Nolan"
    )

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the delete_by_id method
    success = movies_repo.delete_by_id("tt1375666")

    # Assert that the movie is deleted successfully
    assert success is True
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_delete_movie_by_id_no_match(mock_session):
    # Mocking the query method of the session
    mock_session.query().filter_by().first.return_value = None

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the delete_by_id method
    success = movies_repo.delete_by_id("tt1375666")

    # Assert that the movie is deleted successfully
    assert success is False


def test_delete_movie_by_id_query_exception(mock_session):
    # Mocking the query method of the session
    mock_session.query().filter_by().first.side_effect = Exception()

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the delete_by_id method
    success = movies_repo.delete_by_id("tt1375666")

    # Assert that the movie is deleted successfully
    assert success is False
    mock_session.rollback.assert_called_once()


def test_get_all_movies(mock_session):

    # Create movie instances
    movie_instance_1 = MovieModel(imdb_id="tt0166222", title="Inception")
    movie_instance_2 = MovieModel(imdb_id="tt6181728", title="Interstellar")

    # Define the expected data
    expected_data = [
        {"imdbID": "tt0166222", "Title": "Inception"},
        {"imdbID": "tt6181728", "Title": "Interstellar"},
    ]
    # Set up the mock behavior for query, order_by, offset, limit, and all methods
    mock_query = MagicMock()
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [movie_instance_1, movie_instance_2]
    mock_session.query.return_value = mock_query

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the get_all method
    response = movies_repo.get_all(limit=5)

    assert len(response) == 2
    assert response[0]["imdbID"] == expected_data[0]["imdbID"]
    assert response[0]["Title"] == expected_data[0]["Title"]
    assert response[1]["imdbID"] == expected_data[1]["imdbID"]
    assert response[1]["Title"] == expected_data[1]["Title"]

    # Assert that the query method of the session is called once with the correct arguments
    mock_session.query.assert_called_once_with(MovieModel)

    # Assert that the limit method of the query object is called once with the correct arguments
    mock_query.limit.assert_called_once_with(5)

    # Assert that the all method of the query object is called once
    mock_query.all.assert_called_once()


def test_is_database_empty_returns_true_when_empty(mock_session):
    # Mocking the count method of the query to return zero records
    mock_query = mock_session.query.return_value
    mock_query.count.return_value = 0

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the is_database_empty method
    is_empty = movies_repo.is_database_empty()

    # Assert that the method returns True
    assert is_empty is True


def test_is_database_empty_table_not_exist(mock_session):
    # Mocking the count method of the query to return zero records
    mock_query = mock_session.query.return_value
    mock_query.count.return_value = 0

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)
    mock_query.count.side_effect = OperationalError(
        statement="Mocked error", params={}, orig=BaseException()
    )

    # Call the is_database_empty method
    is_empty = movies_repo.is_database_empty()

    # Assert that the method returns True
    assert is_empty is True


def test_is_database_empty_database_error(mock_session):
    # Mocking the count method of the query to return zero records
    mock_query = mock_session.query.return_value
    mock_query.count.return_value = 0

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)
    mock_query.count.side_effect = Exception()

    # Call the is_database_empty method
    is_empty = movies_repo.is_database_empty()

    # Assert that the method returns True
    assert is_empty is True


def test_is_database_empty_returns_false_when_not_empty(mock_session):
    # Mocking the count method of the query to return non-zero records
    mock_query = mock_session.query.return_value
    mock_query.count.return_value = 5

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the is_database_empty method
    is_empty = movies_repo.is_database_empty()

    # Assert that the method returns False
    assert is_empty is False
