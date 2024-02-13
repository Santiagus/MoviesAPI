import requests
import time


def measure_response_time(base_url: str, num_requests: int, title: str = ""):
    """
    Measure the average response time for making requests to the FastAPI endpoints.

    Parameters:
    - `base_url` (str): The base URL of the FastAPI application.
    - `num_requests` (int): The number of requests to send.
    - `title` (str, optional): The title of the movie for the `/movie/{title}` endpoint.

    Returns:
    - dict: A dictionary containing the average response times for the endpoints.

    """
    # Define the endpoint URLs
    movies_url = f"{base_url}/movies"
    movie_url = f"{base_url}/movie/{title}"

    # Measure the response time for the /movies endpoint
    start_time = time.time()
    for _ in range(num_requests):
        response = requests.get(movies_url)
    end_time = time.time()
    avg_movies_response_time = (end_time - start_time) / num_requests

    # Measure the response time for the /movie/{title} endpoint
    if title:
        start_time = time.time()
        for _ in range(num_requests):
            response = requests.get(movie_url)
        end_time = time.time()
        avg_movie_response_time = (end_time - start_time) / num_requests
    else:
        avg_movie_response_time = None

    return {
        "avg_movies_response_time": avg_movies_response_time,
        "avg_movie_response_time": avg_movie_response_time,
    }


# Define the base URL of your FastAPI application
base_url = "http://127.0.0.1:8000"

# Define the number of requests to send
num_requests = 100

# Define the title of the movie to check
title = "The Wonderful World of Disney: 40 Years of Television Magic"

# Measure the response time for the endpoints
response_times = measure_response_time(base_url, num_requests, title)
print(
    f"Avg. response time for /movies: {response_times['avg_movies_response_time']} seconds"
)
print(
    f"Avg. response time for /movie/{title}: {response_times['avg_movie_response_time']} seconds"
)
