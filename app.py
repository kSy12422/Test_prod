import json
import logging

import redis
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyQuery

logging.basicConfig(level=logging.INFO)

app = FastAPI()

API_TOKEN = "your_api_token_here"
REDIS_CLIENT = redis.Redis(host="localhost", port=6379, db=0)


def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


@app.post("/search")
async def search(url: str, phrase: str, token: str = Security(APIKeyQuery(name="token"))):
    logging.info(f"Received search request for URL {url} and phrase {phrase}")
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
    cache_key = f"search:{url}:{phrase}"
    cached_result = REDIS_CLIENT.get(cache_key)
    if cached_result:
        return JSONResponse(content=cached_result, media_type="application/json")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        if phrase.lower() in text.lower():
            distance = levenshtein_distance(phrase, text)
            result = {"found": True, "distance": distance}
        else:
            result = {"found": False}
        REDIS_CLIENT.setex(cache_key, 3600, json.dumps(result))  # cache for 1 hour
        return result
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error fetching URL")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

