import requests

r = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php")
print(r.status_code)
print(r.text[:200])
