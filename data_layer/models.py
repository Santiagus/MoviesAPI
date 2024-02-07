from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MovieModel(Base):
    """
    Model representing a movie.

    Attributes:
        imdb_id (str): The IMDb ID of the movie (primary key).
        title (str): The title of the movie.
        year (str): The release year of the movie.
        rated (str): The rating of the movie.
        released (str): The release date of the movie.
        runtime (str): The duration of the movie.
        genre (str): The genre of the movie.
        director (str): The director(s) of the movie.
        writer (str): The writer(s) of the movie.
        actors (str): The actor(s) of the movie.
        plot (str): The plot summary of the movie.
        language (str): The language of the movie.
        country (str): The country where the movie was produced.
        awards (str): The awards received by the movie.
        poster (str): The URL of the movie poster.
        ratings (list): The ratings received by the movie.
        metascore (str): The metascore of the movie.
        imdb_rating (str): The IMDb rating of the movie.
        imdb_votes (str): The number of IMDb votes received by the movie.
        type (str): The type of the movie (e.g., movie, series).
        dvd (str): The DVD release date of the movie.
        box_office (str): The box office earnings of the movie.
        production (str): The production company of the movie.
        website (str): The official website of the movie.
        response (str): The response status of the movie.
    """

    __tablename__ = "movies"

    imdb_id = Column(String, primary_key=True)
    title = Column(String)
    year = Column(String)
    rated = Column(String)
    released = Column(String)
    runtime = Column(String)
    genre = Column(String)
    director = Column(String)
    writer = Column(String)
    actors = Column(String)
    plot = Column(Text)
    language = Column(String)
    country = Column(String)
    awards = Column(String)
    poster = Column(String)
    ratings = Column(JSON)
    metascore = Column(String)
    imdb_rating = Column(String)
    imdb_votes = Column(String)
    type = Column(String)
    dvd = Column(String)
    box_office = Column(String)
    production = Column(String)
    website = Column(String)

    def __repr__(self):
        """
        Return a string representation of the movie.

        Returns:
            str: A string containing selected attributes of the movie.
        """
        attributes = {
            "Title": self.title,
            "Year": self.year,
            "imdbID": self.imdb_id,
            "Type": self.type,
            "Poster": self.poster,
        }
        return str(attributes)

    def to_dict(self):
        """
        Convert the movie attributes to a dictionary.

        Returns:
            dict: A dictionary containing all attributes of the movie.
        """
        return {
            "Title": self.title,
            "Year": self.year,
            "Rated": self.rated,
            "Released": self.released,
            "Runtime": self.runtime,
            "Genre": self.genre,
            "Director": self.director,
            "Writer": self.writer,
            "Actors": self.actors,
            "Plot": self.plot,
            "Language": self.language,
            "Country": self.country,
            "Awards": self.awards,
            "Poster": self.poster,
            "Ratings": self.ratings,
            "Metascore": self.metascore,
            "imdbRating": self.imdb_rating,
            "imdbVotes": self.imdb_votes,
            "imdbID": self.imdb_id,
            "Type": self.type,
            "DVD": self.dvd,
            "BoxOffice": self.box_office,
            "Production": self.production,
            "Website": self.website,
        }
