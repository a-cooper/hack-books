
import requests
import json
from bs4 import BeautifulSoup
from html.parser import HTMLParser

WIKIDATA_SEARCH = "https://www.wikidata.org/w/api.php?action=query&format=json&list=search"
WIKIDATA_PARSE = "https://www.wikidata.org/wiki/Special:EntityData/"
GENDER_MAP_JSON = "reference_data/gender_mapping.json"
COUNTRY_MAP_JSON = "reference_data/country_mapping.json"

NATIONALITY = "country of citizenship"
GENDER = "sex or gender"

class ReferenceData():
    def __init__(self):
        with open(GENDER_MAP_JSON) as f:
            self.gender_map = json.load(f)

        with open(COUNTRY_MAP_JSON) as f:
            self.country_map = json.load(f)

    def get_gender(self, id: str):
        gender = self.gender_map.get(id)
        if gender:
            return gender
        # TODO have it look up the value
        return "Unknown"

    def get_country(self, id: str):
        country = self.country_map.get(id)
        if country:
            return country
        # TODO have it look up the value
        return "Unknown"

    def update_gender_map(self, key: str, value: str):
        self.gender_map.put(key, value)
        with open('reference_data/gender_mapping.json', 'w') as f:
            json.dump(GENDER_MAP_JSON, f)



def test_request():
    response = requests.get("https://www.wikidata.org/w/api.php?action=query&list=search&srsearch=Akwaeke%20Emezi&format=json")
    print(response)


def get_page_id(text: str):
    """
    Finds a page for our search term
    :param text: A string to search
    :return: the pageid of the top result in the search
    """
    response = requests.get(WIKIDATA_SEARCH + "&srsearch=" + text)
    data = json.loads(response.text)
    top_page = data.get("query").get("search")[0]
    return top_page.get("title")


def get_page_info(pageid: str):
    response = requests.get(WIKIDATA_PARSE + pageid + ".json")
    data = json.loads(response.text)
    properties = data.get("entities").get(pageid).get("claims")
    get_gender(properties)
    get_nationality(properties)

#def extract_pageid()

def get_gender(data: dict):
    gender = data.get("P21")[0].get("mainsnak").get("datavalue").get("value").get("id")
    print(reference.get_gender(gender))


def get_nationality(data: dict):
    nationality = data.get("P27")[0].get("mainsnak").get("datavalue").get("value").get("id")
    print(reference.get_country(nationality))

reference = ReferenceData()
id = get_page_id("Akwaeke Emezi")
get_page_info(id)


