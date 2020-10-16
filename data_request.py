
import requests
import json
from bs4 import BeautifulSoup
import re

WIKIDATA_SEARCH = "https://www.wikidata.org/w/api.php?action=query&format=json&list=search"
WIKIDATA_PARSE = "https://www.wikidata.org/w/api.php?action=parse"

NATIONALITY = "country of citizenship"
GENDER = "sex or gender"

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
    response = requests.get(WIKIDATA_PARSE + "&page=" + pageid)
    soup = BeautifulSoup(response.text, 'lxml')
    get_gender(response.text)
    #print(soup.body.div)

#def extract_pageid()

def get_gender(data: str):
    start = "<a title=\"Property:P21\" href=\"/wiki/Property:P21\">sex or gender</a>"
    end = "<<a title=\"Property:\">"
    result = re.findall(r".*", data)
    #data = soup.find_all(string=re.compile('P21'))
    print(result)



id = get_page_id("Akwaeke Emezi")
get_page_info(id)

