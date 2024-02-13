from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class UnitOfWork:
    """
    Unit of Work pattern for managing database sessions.

    Attributes:
    - `database` (str): The database connection string.
    - `session_maker` (sqlalchemy.orm.session.sessionmaker): The session maker object.

    Methods:
    - `__init__(database)`: Initialize the UnitOfWork with the given database connection string.
    - `__enter__()`: Enter the context manager and return the UnitOfWork instance.
    - `__exit__(exc_type, exc_val, traceback)`: Exit the context manager and close the session.
    - `commit()`: Commit the current transaction.
    - `rollback()`: Rollback the current transaction.
    """

    def __init__(self, database="sqlite:///:memory:"):
        """
        Initialize the UnitOfWork with the given database connection string.

        Parameters:
        - `database` (str): The database connection string.
        """
        self.session_maker = sessionmaker(bind=create_engine(database))

    def __enter__(self):
        """
        Enter the context manager and return the UnitOfWork instance.
        """
        self.session = self.session_maker()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        """
        Exit the context manager and close the session.

        Parameters:
        - `exc_type`: The exception type.
        - `exc_val`: The exception value.
        - `traceback`: The traceback object.
        """
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self):
        """
        Commit the current transaction.
        """
        self.session.commit()

    def rollback(self):
        """
        Rollback the current transaction.
        """
        self.session.rollback()
