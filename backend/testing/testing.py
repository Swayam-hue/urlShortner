# for testing purposes
import hashlib as hash
from fastapi.responses import RedirectResponse
import redis
import urllib3 as check

url = "https://urlshortner.fastapicloud.dev/gb"
r = redis.Redis.from_url("rediss://default:gQAAAAAAAhl-AAIgcDFmZTY5NmJhYjEwODM0MzBjODY3ZDk3MDAzODQ4ZTMzMg@live-goshawk-137598.upstash.io:6379",
                         decode_responses = True)

# print(r.ping())
    

# hexValue = hash.sha256(url.encode()).hexdigest()

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

def checkLength(url):
    code = url[37:]
    print(type(code))
    print(code)

checkLength(url)


# print(encode_string_base62(url))

