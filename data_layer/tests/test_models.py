import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_layer.models import (
    MovieModel,
)


# Define a fixture to set up the SQLAlchemy engine and session
@pytest.fixture(scope="module")
def db_session():
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create the database schema
    MovieModel.metadata.create_all(engine)

    yield session

    # Clean up after the test session
    session.close()
    MovieModel.metadata.drop_all(engine)


def test_movie_model(db_session):
    # Create a movie instance
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

    # Transform keys to snake case
    transformed_data = {key.lower(): value for key, value in movie_data.items()}

    movie = MovieModel(**transformed_data)

    # Add the movie to the session
    db_session.add(movie)
    db_session.commit()

    # Retrieve the movie from the session
    retrieved_movie = (
        db_session.query(MovieModel).filter_by(imdb_id="tt0362300").first()
    )

    # Assert that the retrieved movie matches the original movie
    assert retrieved_movie.imdb_id == movie_data["imdb_id"]
    assert retrieved_movie.title == movie_data["title"]
    assert retrieved_movie.year == movie_data["year"]
    assert retrieved_movie.title == movie_data["title"]
    assert retrieved_movie.year == movie_data["year"]
    assert retrieved_movie.rated == movie_data["rated"]
    assert retrieved_movie.released == movie_data["released"]
    assert retrieved_movie.runtime == movie_data["runtime"]
    assert retrieved_movie.genre == movie_data["genre"]
    assert retrieved_movie.director == movie_data["director"]
    assert retrieved_movie.writer == movie_data["writer"]
    assert retrieved_movie.actors == movie_data["actors"]
    assert retrieved_movie.plot == movie_data["plot"]
    assert retrieved_movie.language == movie_data["language"]
    assert retrieved_movie.country == movie_data["country"]
    assert retrieved_movie.awards == movie_data["awards"]
    assert retrieved_movie.poster == movie_data["poster"]
    assert retrieved_movie.ratings == movie_data["ratings"]
    assert retrieved_movie.metascore == movie_data["metascore"]
    assert retrieved_movie.imdb_rating == movie_data["imdb_rating"]
    assert retrieved_movie.imdb_votes == movie_data["imdb_votes"]
    assert retrieved_movie.type == movie_data["type"]
    assert retrieved_movie.dvd == movie_data["dvd"]
    assert retrieved_movie.box_office == movie_data["box_office"]
    assert retrieved_movie.production == movie_data["production"]
    assert retrieved_movie.website == movie_data["website"]
    assert retrieved_movie.response == movie_data["response"]
