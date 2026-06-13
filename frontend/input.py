import requests

longURL = input("Enter your URL: ")
# customAlias = input("Enter your custom alias: ")
# expirationDate = input("Enter your expiration date ")

response = requests.post(
    "http://127.0.0.1:8000/hash",
    json = {
        "longURL" : longURL
    }
)

shortCode = response.json()["shortCode"]
shortURL = response.json()["shortURL"]
# print(response.status_code)
# print(response.text)
print(f"Your shortened URL is {shortURL}")

