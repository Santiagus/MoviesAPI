from data_layer.models import MovieModel
from sqlalchemy.exc import OperationalError
import logging


class MoviesRepository:
    """
    Repository class for accessing movie data in the database.

    Attributes:
    - `session`: The SQLAlchemy database session.

    Methods:
    - `is_database_empty()`: Check if the movie table exists and is empty.
    - `add(movie)`: Add a movie to the database.
    - `get_by_id(imdb_id)`: Get a movie by its IMDb ID.
    - `get_by_title(title)`: Get a movie by its title.
    - `get_all(offset=0, limit=100)`: Get all movies in the database.
    - `delete_by_id(imdb_id)`: Delete a movie by its IMDb ID.
    """

    def __init__(self, session):
        """
        Initialize the MoviesRepository with the given database session.

        Parameters:
        - `session`: The SQLAlchemy database session.
        """
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
        """
        Add a movie to the database.

        Parameters:
        - `movie`: The movie object to add to the database.
        """
        self.session.add(movie)

    def get_by_id(self, imdb_id):
        """
        Get a movie by its IMDb ID.

        Parameters:
        - `imdb_id` (str): The IMDb ID of the movie to retrieve.

        Returns:
        - dict or None: A dictionary representing the movie if found, or None if not found.
        """
        result = (
            self.session.query(MovieModel)
            .filter(MovieModel.imdb_id == imdb_id)
            .one_or_none()
        )
        if result:
            return result.to_dict()
        else:
            return None

    def get_by_title(self, title):
        """
        Get a movie by its title.

        Parameters:
        - `title` (str): The title of the movie to retrieve.

        Returns:
        - dict or None: A dictionary representing the movie if found, or None if not found.
        """
        result = (
            self.session.query(MovieModel)
            .filter(MovieModel.title == title)
            .one_or_none()
        )

        if result:
            return result.to_dict()
        else:
            return None

    def get_all(self, offset=0, limit=100):
        """
        Get all movies in the database.

        Parameters:
        - `offset` (int): The offset for pagination.
        - `limit` (int): The maximum number of movies to retrieve.

        Returns:
        - list: A list of dictionaries representing the movies.
        """
        movies = (
            self.session.query(MovieModel)
            .order_by(MovieModel.title)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [movie.to_dict() for movie in movies]

    def delete_by_id(self, imdb_id):
        """
        Delete a movie by its IMDb ID.

        Parameters:
        - `imdb_id` (str): The IMDb ID of the movie to delete.

        Returns:
        - bool: True if the movie was deleted successfully, False otherwise.
        """
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
            return False
