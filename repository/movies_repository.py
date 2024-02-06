from repository.models import MovieModel


class MoviesRepository:
    def __init__(self, session):
        self.session = session

    def add(self, movie):
        self.session = movie

    def get_by_id(self, imdb_id): 
        return (
            self.session.query(MovieModel)
            .filter(MovieModel.imdb_id == imdb_id)
            .one_or_none()
        )

    def get_all(self, limit=None, **filters):
        return self.session.query.filter_by(**filters).limit(limit).all()

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
