import logging
from venv import create
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from contextlib import AsyncExitStack
from movies_service.app import lifespan
from data_fetcher.movie_data_fetcher import MovieDataFetcher


@pytest.mark.asyncio
async def test_lifespan():
    # Mock the FastAPI app instance
    app = MagicMock(FastAPI, create=True)

    # Mock the required attributes and methods of the app
    app.state = MagicMock()

    with patch(
        "movies_service.app.utils.get_database_url_from_alembic_config"
    ) as mock_get_database_url:
        mock_get_database_url.return_value = "mocked_database_url"
        with patch("movies_service.app.UnitOfWork"), patch(
            "movies_service.app.MoviesRepository"
        ), patch("movies_service.app.MovieDataFetcher") as mock_data_fetcher:

            mock_fetch_and_save_movies_data = AsyncMock()
            mock_fetch_and_save_movies_data.return_value = [
                {"Title": "Movie 1", "Year": "2000"},
                {"Title": "Movie 2", "Year": "2001"},
                {"Title": "Movie 3", "Year": "2002"},
            ]

            # Set the mock method as an attribute of the MovieDataFetcher instance
            mock_data_fetcher.return_value.fetch_and_save_movies_data = (
                mock_fetch_and_save_movies_data
            )

            # Execute the lifespan context manager
            async with lifespan(app):
                pass  # You can add test code here if necessary

            mock_get_database_url.assert_called_once()
            app.state.mdf.fetch_and_save_movies_data.assert_called_with("Disney")


@pytest.mark.asyncio
async def test_lifespan_raise_exception():
    # Mock the FastAPI app instance
    app = MagicMock(FastAPI, create=True)

    # Mock the required attributes and methods of the app
    app.state = MagicMock()

    with patch(
        "movies_service.app.utils.get_database_url_from_alembic_config"
    ) as mock_get_database_url:
        mock_get_database_url.return_value = "mocked_database_url"
        with patch("movies_service.app.UnitOfWork"), patch(
            "movies_service.app.MoviesRepository"
        ), patch("movies_service.app.MovieDataFetcher") as mock_data_fetcher:

            mock_fetch_and_save_movies_data = AsyncMock()
            mock_fetch_and_save_movies_data.return_value = [
                {"Title": "Movie 1", "Year": "2000"},
                {"Title": "Movie 2", "Year": "2001"},
                {"Title": "Movie 3", "Year": "2002"},
            ]

            # Set the mock method as an attribute of the MovieDataFetcher instance
            mock_data_fetcher.return_value.fetch_and_save_movies_data = (
                mock_fetch_and_save_movies_data
            )

            # Execute the lifespan context manager
            async with lifespan(app):
                pass  # You can add test code here if necessary

            mock_get_database_url.assert_called_once()
            app.state.mdf.fetch_and_save_movies_data.assert_called_with("Disney")
