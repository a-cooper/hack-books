
import requests
import json
import csv

WIKIDATA_SEARCH = "https://www.wikidata.org/w/api.php?action=query&format=json&list=search"
WIKIDATA_PARSE = "https://www.wikidata.org/wiki/Special:EntityData/"
GENDER_MAP_JSON = "reference_data/gender_mapping.json"
COUNTRY_MAP_JSON = "reference_data/country_mapping.json"
CONTINENT_MAP_JSON = "reference_data/continent_mapping.json"
AUTHOR_MAP_JSON = "reference_data/author_mapping.json"

class ReferenceData():
    def __init__(self):
        with open(GENDER_MAP_JSON) as f:
            self.gender_map = json.load(f)

        with open(COUNTRY_MAP_JSON) as f:
            self.country_map = json.load(f)

        with open(AUTHOR_MAP_JSON) as f:
            self.author_map = json.load(f)


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
        else:
            country = {}
            country_data = json.loads(requests.get(WIKIDATA_PARSE + id + ".json").text)
            data = country_data.get("entities").get(id)
            country_name = data.get("labels").get("en").get("value")
            country["name"] = country_name
            try:
                region = data.get("claims").get("P361")[0].get("mainsnak").get("datavalue").get("value").get("id") # P361 is the 'part of' tag
                region_name = self.get_regions(region)
                country["region"] = region_name
            except TypeError:
                country["region"] = "Unknown"
            self.country_map[id] = country
            return country

    def get_regions(self, id: str):
        region_data = json.loads(requests.get(WIKIDATA_PARSE + id + ".json").text)
        data = region_data.get("entities").get(id)
        region_name = data.get("labels").get("en").get("value")
        #continent_id = data.get("claims").get("P30")[0].get("mainsnak").get("datavalue").get("value").get("id")
        return region_name #, self.continent_map.get(continent_id)


    def update_gender_map(self, key: str, value: str):
        self.gender_map.put(key, value)


    def update_maps_jsons(self):
        with open(GENDER_MAP_JSON, 'w') as f:
            json.dump(self.gender_map, f)
        with open(COUNTRY_MAP_JSON, 'w') as f:
            json.dump(self.country_map, f)
        with open(AUTHOR_MAP_JSON, 'w') as f:
            json.dump(self.author_map, f)

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

    pages = data.get("query").get("search")
    if len(pages) < 1:
        return -1
    top_page = pages[0]
    return top_page.get("title")


def get_author_info(author: str):
    author_details = reference.author_map.get(author)
    if author_details:
        return author_details
    pageid = get_page_id(author)
    if pageid == -1:
        author_details = {"id": "Unknown", "gender": "Unknown", "country": "Unknown", "region": "Unknown"}
    else:
        response = requests.get(WIKIDATA_PARSE + pageid + ".json")
        data = json.loads(response.text)
        properties = data.get("entities").get(pageid).get("claims")
        author_details = {"id": pageid, "gender": get_gender(properties)}
        country_details = get_nationality(properties)
        author_details["country"] = country_details.get("name")
        author_details["region"] = country_details.get("region")

    reference.author_map[author] = author_details
    return author_details

#def extract_pageid()

def get_gender(data: dict):
    try:
        gender = data.get("P21")[0].get("mainsnak").get("datavalue").get("value").get("id")
    except TypeError:
        return "Unknown"
    return reference.get_gender(gender)


def get_nationality(data: dict):
    try:
        country = data.get("P27")[0].get("mainsnak").get("datavalue").get("value").get("id")
    except TypeError:
        return {"country":"Unknown", "region":"Unknown"}
    return reference.get_country(country)


def read_goodreads(filename: str):
    author_field_index = 0
    authors = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for index, field in enumerate(fields):
            if field.lower() == "author":
                author_field_index = index
                break
        for row in csvreader:
            authors.append(row[author_field_index])
    for index, author in enumerate(authors):
        if author:
            print("author: " + author + "  "+ str(get_author_info(author)))
        if index%5 == 0:
            reference.update_maps_jsons()
    reference.update_maps_jsons()



reference = ReferenceData()
read_goodreads("goodreads/la_goodreads_library_export.csv")
#get_author_info("Jules Verne")
#reference.update_maps_jsons()


