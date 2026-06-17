from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import hashlib as hash
import psycopg2
import redis
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()



r = redis.Redis.from_url(os.getenv("REDIS_URL"),
                         decode_responses = True)

mydb = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
    sslmode="require"
)

mycursor = mydb.cursor()

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

class URLRequest(BaseModel):
    longURL: str

def existingShortURLCheck(url):
    code = url[37:]
    mycursor.execute("select 1 from urltable_2 where shortcode = %s",
                     (code,))
    result = mycursor.fetchone()

    if result:
        return True
    else:
        return False

def encode(num, alphabet):
    base = len(alphabet)
    if num == 0:
        return alphabet[0]
    encoded = ""
    while num > 0:
        num, rem = divmod(num, base)
        encoded = alphabet[rem] + encoded
    return encoded

def encode_string_base62(input_string):
    # Hash the string to get a large integer
    hexValue = hash.sha256(input_string.encode()).hexdigest()
    hash_int = int(hexValue, 16)
    short_code = encode(hash_int, BASE62)[:8]
    return short_code

def id_counter():
    id = r.incr("url_counter")
    return encode(id, BASE62)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://url-shortner-hizq.vercel.app",
        "https://url-shortner-hizq-ifmnnt7gu-swayam-hues-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# class ABC(BaseModel):
#     longURL: str

@app.get("/")
def home(request: Request):
    return {
        "short_url": None
    }


@app.post("/hash")
def shortURL(data: URLRequest):
    url = data.longURL

    # If the shortURL is submitted again by the user
    flag = existingShortURLCheck(url)
    if flag == True:
        code = url[37:]
        return {
             "remark" : f"The link has already been shortened. Here is the same link : ",
             "short_url": f"https://urlshortner.fastapicloud.dev/{code}"
        }
        
    
    mycursor.execute("select shortCode from urltable_2 where longURL = %s",
                     (url,))
    
    result = mycursor.fetchone()

    if result:
        print("URL already exists.")

        return {
             "remark" : f"URL already exists. Here is the shortened link:",
             "short_url": f"https://urlshortner.fastapicloud.dev/{result[0]}"
        }


    
    shortCode = id_counter()
    mycursor.execute("INSERT INTO urltable_2 (longURL, shortCode) VALUES (%s, %s)",
                     (url, shortCode))
    mydb.commit()

    # Storing the mapping in Redis Cache
    r.setex(
    f"url:{shortCode}",
    86400,
    url
)

    return {
        "remark": f"Here is your shortened link",
        "short_url": f"https://urlshortner.fastapicloud.dev/{shortCode}"
    }


@app.get("/{shortCode}")
def getRedirectURL(shortCode : str):

    # Checking in Redis cache for the mapping
    cached_url = r.get(f"url : {shortCode}")

    if cached_url:
        print("Cache hit")
        return RedirectResponse(
            url = cached_url,
            status_code = 302
        )
    
    print("Cache miss")
        
    mycursor.execute("select longURL from urltable_2 where shortCode = %s",
                     (shortCode,))
    result = mycursor.fetchone()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )
    
    longURL = result[0]
    r.set(
        f"url : {shortCode}",
        longURL
    )


    return RedirectResponse(
        url = result[0],
        status_code = 302
    )


