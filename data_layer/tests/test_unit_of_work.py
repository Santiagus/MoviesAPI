import unittest
from unittest.mock import Mock
from sqlalchemy import inspect
from data_layer.unit_of_work import UnitOfWork
from data_layer.models import MovieModel


class TestUnitOfWork(unittest.TestCase):
    """
    Unit tests for the UnitOfWork class.

    Methods:
        setUp(): Set up the test environment before each test method is executed.
        test_table_created(): Test if the database table is created successfully.
        test_commit(): Test the commit functionality of the UnitOfWork class.
        test_rollback(): Test the rollback functionality of the UnitOfWork class.
    """

    def setUp(self):
        """
        Set up the test environment before each test method is executed.
        """
        self.database = "sqlite:///:memory:"

        # Create an instance of UnitOfWork
        self.uow = UnitOfWork(self.database)
        with self.uow as uow:
            self.session = uow.session
        self.engine = self.session.bind

        # Create all tables defined in the models
        MovieModel.metadata.create_all(self.engine)

    def test_table_created(self):
        """
        Test if the database table is created successfully.
        """
        inspector = inspect(self.engine)
        if inspector is not None:
            tables = inspector.get_table_names()

        self.assertIn("movies", tables)

    def test_commit(self):
        """
        Test the commit functionality of the UnitOfWork class.
        """
        self.session.add(MovieModel(title="Test Movie", imdb_id="tt123456"))
        self.uow.commit()
        movie = self.session.query(MovieModel).filter_by(imdb_id="tt123456").first()
        self.assertIsNotNone(movie)

    def test_rollback(self):
        """
        Test the rollback functionality of the UnitOfWork class.
        """
        self.session.add(MovieModel(title="Test Movie", imdb_id="tt123456"))
        self.uow.rollback()
        movie = self.session.query(MovieModel).filter_by(imdb_id="tt123456").first()
        self.assertIsNone(movie)

    def test_exit_without_exception(self):
        session_mock = Mock()
        unit_of_work = UnitOfWork()
        unit_of_work.session = session_mock

        unit_of_work.__exit__(None, None, None)

        session_mock.close.assert_called_once()

    def test_exit_with_exception(self):
        session_mock = Mock()
        unit_of_work = UnitOfWork()
        unit_of_work.session = session_mock

        unit_of_work.__exit__(Exception, Exception("Test Exception"), None)

        session_mock.rollback.assert_called_once()
        session_mock.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
