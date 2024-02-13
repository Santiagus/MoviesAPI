import logging
import json
from fastapi import HTTPException, Query, Depends, status, Header, Response, status
from sqlalchemy import false
from data_layer.unit_of_work import UnitOfWork
from movies_service.app import app
from data_layer.movies_repository import MoviesRepository
from fastapi.security.api_key import APIKeyHeader
from fastapi_cache.decorator import cache


@app.get("/movies")
@cache(expire=60)
async def get_all_movies(
    limit: int = Query(10, title="The number of movies to retrieve", ge=1),
    page: int = Query(1, title="Results page", ge=1),
):
    with UnitOfWork(app.state.database_url) as unit_of_work:
        repo = MoviesRepository(unit_of_work.session)
        if not repo.is_database_empty():
            offset = (page - 1) * limit
            return repo.get_all(offset, limit)
        else:
            logging.warning("Movies not found in the database")
            raise HTTPException(
                status_code=404, detail="Movies not found in the database"
            )


@app.get("/movie/{title}")
@cache(expire=60)
async def get_movie(title: str):
    with UnitOfWork(app.state.database_url) as unit_of_work:
        repo = MoviesRepository(unit_of_work.session)
        if not repo.is_database_empty():
            movie = repo.get_by_title(title)
            if not movie:
                raise HTTPException(
                    status_code=404,
                    detail=f'No exact match for "{title}" in the database.',
                )
            return movie
        else:
            logging.warning("Movie not found in the database")
            raise HTTPException(
                status_code=404, detail="Movie not found in the database"
            )


@app.post("/movie/{title}")
async def add_movie(title: str):
    try:
        result = await app.state.mdf.fetch_and_save_movies_data(title, limit=1)
        if result is None:
            return Response(
                content=json.dumps({"detail": f"No match found for {title}"}),
                status_code=status.HTTP_404_NOT_FOUND,
                media_type="application/json",
            )
        # Saved first matching title movie
        if result[0] is not None:
            return Response(
                content=json.dumps({"detail": f"Saved {result}"}),
                status_code=status.HTTP_201_CREATED,
                media_type="application/json",
            )
        # Fist movie title coincidende is already in the database
        else:
            return Response(
                content=json.dumps(
                    {"detail": f"{title} already exists in the database"}
                ),
                status_code=status.HTTP_200_OK,
                media_type="application/json",
            )
    except Exception as e:
        # Handle exceptions raised during fetch_and_save_movies_data
        return Response(
            content=json.dumps({"detail": f"An error occurred: {e}"}),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json",
        )


# Dummy database of API keys
api_keys = {"Movies_API_KEY_number_1"}


def is_api_key_valid(api_key: str = Header(None)):
    """Dependency function to verify the API key."""
    return api_key in api_keys


# Define the API key security scheme
APIKeyAuth = APIKeyHeader(name="Authorization", auto_error=False)


@app.delete("/movie/{imdb_id}")
async def delete_movie(imdb_id: str, api_key: str = Depends(APIKeyAuth)):
    if not is_api_key_valid(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

    with UnitOfWork(app.state.database_url) as unit_of_work:
        repo = MoviesRepository(unit_of_work.session)
        result = repo.delete_by_id(imdb_id)
        if result:
            return {"detail": f"Movie with ID {imdb_id} was deleted successfully"}
        logging.warning("Movie not found in the database")
        raise HTTPException(status_code=404, detail="Movie not found in the database")
