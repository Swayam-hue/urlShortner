import redis

r = redis.Redis(
    host = "localhost",
    port = 6379,
    decode_responses=True
)

url = "https://redis.io/docs/latest/commands/incr/"
r.set("url_counter", 1000)

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
    id = r.incr("url_counter")
    return encode(id, BASE62)

short_code = id_counter()

print("URL : ", url)
print("Short Code : ", short_code)
print("Current Counter : ", r.get("url_counter"))