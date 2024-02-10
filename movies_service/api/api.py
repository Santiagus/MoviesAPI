from movies_service.app import app

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
def get_all_movies():
    return movies_data


@app.get("/movie/{title}")
def get_movie(title: str):
    return movies_data[0]


@app.post("/movie/{title}")
def add_movie(title: str):
    return {"Added": movies_data[0]}


@app.delete("/movie/{imdb_id}")
def delete_movie(imdb_id: str):
    return {"Deleted": imdb_id}
