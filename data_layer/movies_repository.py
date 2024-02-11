from data_layer.models import MovieModel
from sqlalchemy.exc import OperationalError
import logging


class MoviesRepository:
    def __init__(self, session):
        self.session = session

    def is_database_empty(self):
        """
        Check if the MovieModel table exists and it is empty
        Returns:
            bool: True if the table is empty or it does not exists, False otherwise.
        """
        try:
            num_records = self.session.query(MovieModel).count()
            return num_records == 0
        except OperationalError:
            # Handle the case where the table does not exist
            logging.info("The movies table does not exist in the database.")
            return True
        except Exception as e:
            logging.error(f"Error : {e}")
            return True

    def add(self, movie):
        self.session.add(movie)

    def get_by_id(self, imdb_id):
        return (
            self.session.query(MovieModel)
            .filter(MovieModel.imdb_id == imdb_id)
            .one_or_none()
        )

    def get_by_title(self, title):
        return (
            self.session.query(MovieModel)
            .filter(MovieModel.title == title)
            .one_or_none()
        )

    def get_all(self, offset=0, limit=100):
        movies = (
            self.session.query(MovieModel)
            .order_by(MovieModel.title)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [movie.to_dict() for movie in movies]

    def delete_by_id(self, imdb_id):
        try:
            # Query the movie by imdb_id
            movie = self.session.query(MovieModel).filter_by(imdb_id=imdb_id).first()
            if movie:
                # Delete the movie if found
                self.session.delete(movie)
                self.session.commit()
                return True
            else:
                return False
        except Exception as e:
            # Handle exceptions
            self.session.rollback()
            return False, str(e)
