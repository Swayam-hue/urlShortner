from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import mysql.connector
import hashlib as hash
import psycopg2
import os

mydb = psycopg2.connect(
    host="aws-1-ap-northeast-1.pooler.supabase.com",
    database="postgres",
    user="postgres.dnobgpeivluejnlswmff",
    password="@Swayamghosh2005",
    port=6543,
    sslmode="require"
)

mycursor = mydb.cursor()

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

def encode_string_base62(input_string):
    # Hash the string to get a large integer
    hexValue = hash.sha256(input_string.encode()).hexdigest()
    hash_int = int(hexValue, 16)
    short_code = encode(hash_int, BASE62)[:8]
    return short_code

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# class ABC(BaseModel):
#     longURL: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "short_url": None
    }
)

@app.post("/hash", response_class=HTMLResponse)
def shortURL(request : Request,
             longURL : str = Form(...)):
    url = longURL

    mycursor.execute("select shortCode from urltable where longURL = %s",
                     (url,))
    
    result = mycursor.fetchone()

    if result:
        print("URL already exists.")

        return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
             "short_url": f"http://127.0.0.1:8000/{result[0]}"
        }
)

    
    shortCode = encode_string_base62(url)
    mycursor.execute("INSERT INTO urltable (longURL, shortCode) VALUES (%s, %s)",
                     (url, shortCode))
    mydb.commit()
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "short_url": f"http://127.0.0.1:8000/{shortCode}"
    }
)

@app.get("/{shortCode}")
def getRedirectURL(shortCode : str):
    mycursor.execute("select longURL from urltable where shortCode = %s",
                     (shortCode,))
    result = mycursor.fetchone()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )
    
    return RedirectResponse(
        url = result[0],
        status_code = 302
    )
