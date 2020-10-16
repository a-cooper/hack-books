
import requests
import json

WIKIDATA = "https://www.wikidata.org/w/api.php?action=query&format=json"
SEARCH = "&list=search"


def test_request():
    response = requests.get("https://www.wikidata.org/w/api.php?action=query&list=search&srsearch=Akwaeke%20Emezi&format=json")
    print(response)


def search_text(text: str):
    response = requests.get(WIKIDATA + SEARCH + "&srsearch=" + text)
    data = json.loads(response.text)
    print(data)

#def extract_pageid()


search_text("Akwaeke Emezi")

