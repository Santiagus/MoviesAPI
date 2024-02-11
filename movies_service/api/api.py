import logging
from fastapi import HTTPException, Query
from data_layer.unit_of_work import UnitOfWork
from movies_service.app import app
from data_layer.movies_repository import MoviesRepository

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
def get_movie(title: str):
    return movies_data[0]


@app.post("/movie/{title}")
def add_movie(title: str):
    return {"Added": movies_data[0]}


@app.delete("/movie/{imdb_id}")
def delete_movie(imdb_id: str):
    return {"Deleted": imdb_id}
