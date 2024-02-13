import requests
import time

# Define the base URL of your FastAPI application
base_url = "http://127.0.0.1:8000"

# Define the endpoint URLs
title = "The Wonderful World of Disney: 40 Years of Television Magic"
movies_url = f"{base_url}/movies"
movie_url = f"{base_url}/movie/{title}"

# Define the number of requests to send
num_requests = 100

# Measure the response time for the /movies endpoint
start_time = time.time()
for _ in range(num_requests):
    response = requests.get(movies_url)
end_time = time.time()
avg_response_time = (end_time - start_time) / num_requests
print(f"Avg. response time for /movies: {avg_response_time} seconds")

# Measure the response time for the /movie/{title} endpoint
start_time = time.time()
for _ in range(num_requests):
    response = requests.get(movie_url)
end_time = time.time()
avg_response_time = (end_time - start_time) / num_requests
print(f"Avg. response time for /movie/{title}: {avg_response_time} seconds")
