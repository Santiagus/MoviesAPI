import pytest
from unittest.mock import Mock, PropertyMock
from data_layer.models import MovieModel
from data_layer.movies_repository import MoviesRepository


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

    # Assert that the returned movie has the correct attributes
    assert movie.title == "Inception"
    assert movie.year == "2010"
    assert movie.director == "Christopher Nolan"


def test_delete_movie_by_id(mock_session):
    # Mocking the query method of the session
    mock_session.query().filter_by().first.return_value = MovieModel(
        imdb_id="tt1375666", title="Inception", year=2010, director="Christopher Nolan"
    )

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the delete_by_id method
    success, message = movies_repo.delete_by_id("tt1375666")

    # Assert that the movie is deleted successfully
    assert success is True
    assert message == "Movie deleted successfully"


def test_get_all_movies(mock_session):
    # Mocking the query method of the session
    query_mock = Mock()
    type(mock_session).query = PropertyMock(return_value=query_mock)

    # Mocking the limit method of the query
    limit_mock = query_mock.limit.return_value

    # Mocking the all() method to return movie instances
    limit_mock.all.return_value = [
        MovieModel(
            imdb_id="tt1375666",
            title="Inception",
            year=2010,
            director="Christopher Nolan",
        ),
        MovieModel(
            imdb_id="tt0816692",
            title="Interstellar",
            year=2014,
            director="Christopher Nolan",
        ),
    ]

    # Create a repository instance with the mocked session
    movies_repo = MoviesRepository(mock_session)

    # Call the get_all method
    movies = movies_repo.get_all(limit=5)

    # Assert that the correct movies are returned
    assert len(movies) == 2
    assert movies[0].title == "Inception"
    assert movies[1].title == "Interstellar"

    # Assert that the session's query method is called with the correct limit
    query_mock.limit.assert_called_once_with(5)
