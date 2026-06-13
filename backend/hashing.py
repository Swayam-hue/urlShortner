# for testing purposes
import hashlib as hash
from fastapi.responses import RedirectResponse

url = "https://docs.python.org/3/library/hashlib.html"

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


print(encode_string_base62(url))

