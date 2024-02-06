from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MovieModel(Base):
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
    response = Column(String)

    def __repr__(self):
        return f"<Movie(title='{self.title}', year='{self.year}', imdb_id='{self.imdb_id}')>"
