from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from psycopg2.pool import SimpleConnectionPool
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
import redis
import hashlib as hash
import os
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True
)

db_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
    sslmode="require"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    longURL: str

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(num, alphabet):
    base = len(alphabet)

    if num == 0:
        return alphabet[0]

    encoded = ""

    while num > 0:
        num, rem = divmod(num, base)
        encoded = alphabet[rem] + encoded

    return encoded


def id_counter():
    value = r.incr("url_counter")
    return encode(value, BASE62)


def get_connection():
    return db_pool.getconn()


def release_connection(conn):
    db_pool.putconn(conn)


def existing_short_url_check(url: str):

    if not url.startswith(
        "https://urlshortner.fastapicloud.dev/"
    ):
        return False

    code = url.split("/")[-1]

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 1
            FROM urltable_2
            WHERE shortcode = %s
            """,
            (code,)
        )

        return cur.fetchone() is not None

    finally:
        cur.close()
        release_connection(conn)


@app.get("/")
def home():
    return {"status": "alive"}


@app.post("/hash")
def short_url(data: URLRequest):

    url = data.longURL

    conn = get_connection()

    try:
        cur = conn.cursor()

        # Already a shortened URL?
        if existing_short_url_check(url):

            code = url.split("/")[-1]

            return {
                "remark": "Already shortened",
                "short_url": url
            }

        # Check if original URL exists
        cur.execute(
            """
            SELECT shortcode
            FROM urltable_2
            WHERE longURL = %s
            """,
            (url,)
        )

        result = cur.fetchone()

        if result:

            return {
                "remark": "URL already exists",
                "short_url":
                f"https://urlshortner.fastapicloud.dev/{result[0]}"
            }

        short_code = id_counter()

        cur.execute(
            """
            INSERT INTO urltable_2
            (longURL, shortcode)
            VALUES (%s,%s)
            """,
            (url, short_code)
        )

        conn.commit()

        r.setex(
            f"url:{short_code}",
            86400,
            url
        )

        return {
            "remark": "Short URL created",
            "short_url":
            f"https://urlshortner.fastapicloud.dev/{short_code}"
        }

    except Exception as e:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        cur.close()
        release_connection(conn)


@app.get("/{shortCode}")
def redirect_url(shortCode: str):

    cached_url = r.get(f"url:{shortCode}")
    if cached_url:
        print("CACHE HIT")
    else:
        print("CACHE MISS")

    if cached_url:

        return RedirectResponse(
            url=cached_url,
            status_code=302
        )

    conn = get_connection()

    try:

        cur = conn.cursor()

        cur.execute(
            """
            SELECT longURL
            FROM urltable_2
            WHERE shortcode = %s
            """,
            (shortCode,)
        )

        result = cur.fetchone()

        if result is None:

            raise HTTPException(
                status_code=404,
                detail="Short URL not found"
            )

        long_url = result[0]

        r.setex(
            f"url:{shortCode}",
            86400,
            long_url
        )

        return RedirectResponse(
            url=long_url,
            status_code=302
        )

    finally:

        cur.close()
        release_connection(conn)