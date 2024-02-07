from data_layer.models import MovieModel


class MoviesRepository:
    def __init__(self, session):
        self.session = session

    def is_database_empty(self):
        """
        Check if the MovieModel table is empty.
        Returns:
            bool: True if the table is empty, False otherwise.
        """
        num_records = self.session.query(MovieModel).count()
        return num_records == 0

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

    def get_all(self, limit=100):
        movies = self.session.query(MovieModel).limit(limit).all()
        return [movie.to_dict() for movie in movies]

    def delete_by_id(self, imdb_id):
        try:
            # Query the movie by imdb_id
            movie = self.session.query(MovieModel).filter_by(imdb_id=imdb_id).first()
            if movie:
                # Delete the movie if found
                self.session.delete(movie)
                self.session.commit()
                return True, "Movie deleted successfully"
            else:
                return False, "Movie not found"
        except Exception as e:
            # Handle exceptions
            self.session.rollback()
            return False, str(e)
