import logging
from fastapi import HTTPException, Query
from data_layer.unit_of_work import UnitOfWork
from movies_service.app import app
from data_layer.movies_repository import MoviesRepository
from data_fetcher import movie_data_fetcher

# Static movies info  for testing purpose
movies_data = [
    {
        "Title": "Ultimate Fan's Guide to Walt Disney World",
        "Year": "2004",
        "Runtime": "56 min",
        "Type": "movie",
    },
    {
        "Title": "The Shawshank Redemption",
        "Year": "1994",
        "Runtime": "142 min",
        "Type": "movie",
    },
    {
        "Title": "The Godfather",
        "Year": "1972",
        "Runtime": "175 min",
        "Type": "movie",
    },
    {
        "Title": "The Dark Knight",
        "Year": "2008",
        "Runtime": "152 min",
        "Type": "movie",
    },
    {
        "Title": "Pulp Fiction",
        "Year": "1994",
        "Runtime": "154 min",
        "Type": "movie",
    },
]


@app.get("/movies")
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
    mdf = movie_data_fetcher.MovieDataFetcher()
    result = await mdf.fetch_and_save_movies_data(title, limit=1)
    return {"Saved": result}


@app.delete("/movie/{imdb_id}")
async def delete_movie(imdb_id: str):
    return {"Deleted": imdb_id}
