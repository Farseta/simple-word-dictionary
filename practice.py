import requests

api_key = "36454664-87d4-4094-9605-48ffd7241ab1"
word = "apple"
url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'

res =requests.get(url)

definitions = res.json()

for definition in definitions:
    print(definition)