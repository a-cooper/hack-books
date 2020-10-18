import requests
import json
import csv

WIKIDATA_SEARCH = "https://www.wikidata.org/w/api.php?action=query&format=json&list=search"
WIKIDATA_PARSE = "https://www.wikidata.org/wiki/Special:EntityData/"
GENDER_MAP_JSON = "reference_data/gender_mapping.json"
COUNTRY_MAP_JSON = "reference_data/country_mapping.json"
CONTINENT_MAP_JSON = "reference_data/continent_mapping.json"
AUTHOR_MAP_JSON = "reference_data/author_mapping.json"


class AuthorData:
    def __init__(self):
        self._reference = ReferenceData()
        self._writer_words = ["novelist", "author", "writer", ""]
        self._csv_headings = ["Author", "Gender", "Countries"]

    def get_author_info(self, author: str):
        """
        Gets the author information
        :param: str: the author name
        :return: dict: the details of the author
        """
        for writer_word in self._writer_words:
            data = json.loads(requests.get(WIKIDATA_SEARCH + "&srsearch=" + author + " " + writer_word).text)
            pages = data.get("query").get("search")
            if len(pages) >= 1:
                pageid = pages[0].get("title")
                author_details = self._reference.author_map.get(author)
                if author_details:
                    return author_details
                if pageid == -1:
                    continue

                else:
                    response = requests.get(WIKIDATA_PARSE + pageid + ".json")
                    data = json.loads(response.text)
                    if author.lower() not in data.get("entities").get(pageid).get("labels").get("en").get("value").lower():
                        continue
                    else:
                        try:
                            id = data.get("entities").get(pageid).get("claims").get("P31")[0].get("mainsnak").get("datavalue").get("value").get("id")
                            if str(id) != "Q5":  # the id for human
                                continue
                        except IndexError:
                            continue
                    properties = data.get("entities").get(pageid).get("claims")
                    author_details = {"id": pageid, "gender": self.get_gender(properties)}
                    country_details = self.get_country(properties)
                    author_details["country"] = country_details
                    self._reference.author_map[author] = author_details
                    return author_details
        return {"id": "Unknown", "gender": "Unknown", "country": [{"name": "Unknown", "region": "Unknown"}]}

    def get_gender(self, data: dict):
        """
        Returns the gender of the author
        :param (dict): data - a dictionary of the existing author properties
        :return: (str): gender - the gender of the author, or "Unknown" if unknown
        """
        try:
            gender = data.get("P21")[0].get("mainsnak").get("datavalue").get("value").get("id")
        except TypeError:
            return "Unknown"
        return self._reference.get_gender(gender)

    def get_country(self, data: dict):
        """
        Returns the country information o fthe author
        :param data: a dictionary of the existing author properties
        :return: a tuple of the country and region information
        """
        country_entries = data.get("P27")
        if country_entries is None or len(country_entries) == 0:
            country_entries = data.get("P19")
            if country_entries is None or len(country_entries) == 0:
                return [{"country": "Unknown", "region": "Unknown"}]
        countries = []
        for entry in country_entries:
            country = entry.get("mainsnak").get("datavalue").get("value").get("id")
            countries.append(self._reference.get_country(country))
        return countries

    def read_csv(self, filename: str):
        """
        Reads a csv file and extracts the author column
        :param filename: the name of the file as a string
        """
        author_field_index = 0
        authors = []
        author_data = []
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
                data = self.get_author_info(author)
                author_data.append((author, data))
            if index % 10 == 0:  # every 10 entries we write the data to json in case we get a crash
                self._reference.update_maps_jsons()
        self._reference.update_maps_jsons()
        return author_data

    def write_csv(self, filename: str, author_data: list):
        """
        Writes the author_data to a new file
        :param filename: the string of the original filename
        :param author_data: the list of dictionaries of author data
        """
        split_file = filename.split('/')
        new_filename = ""
        for index, component in enumerate(split_file):
            if index == len(split_file) - 1:
                break
            new_filename += component + "/"
        new_filename += "results_" + split_file[-1]
        with open(new_filename, 'w') as csvfile:
            result_writer = csv.writer(csvfile)
            result_writer.writerow(self._csv_headings)
            for author in author_data:
                result_writer.writerow(self.author_data_to_str(author))
        csvfile.close()

    def author_data_to_str(self, author_data: tuple):
        """
        Converts the author_data into a list of strings for sending to csv
        :param author_data: a tuple of string and dict with author info
        :return: the list of strings of the author data
        """
        str_list = [author_data[0], author_data[1].get("gender")]  # first entry in list is author name
        countries = author_data[1].get("country")
        country_str = ""
        if len(countries) == 1 and countries is not None and countries[0].get("name") is not None:
            country_str += countries[0].get("name") + " (" + countries[0].get("region") + ")"
        elif len(countries) > 1:
            for country in countries:
                country_str += country.get("name") + " (" + country.get("region") + ") & "
            country_str = country_str[:-2]
        else:
            country_str = "Unknown"
        str_list.append(country_str)
        return str_list


class ReferenceData:
    """
    The class for handling the reference data json files, as well as doing API calls.
    """

    def __init__(self):
        with open(GENDER_MAP_JSON) as f:
            self.gender_map = json.load(f)

        with open(COUNTRY_MAP_JSON) as f:
            self.country_map = json.load(f)

        with open(AUTHOR_MAP_JSON) as f:
            self.author_map = json.load(f)
        f.close()

    def get_gender(self, id: str):
        gender = self.gender_map.get(id)
        if gender:
            return gender
        return "Unknown"

    def get_country(self, country_id: str):
        country = self.country_map.get(country_id)
        if country:
            return country
        else:
            country = {}
            country_data = json.loads(requests.get(WIKIDATA_PARSE + country_id + ".json").text)
            data = country_data.get("entities").get(country_id)
            country_name = data.get("labels").get("en").get("value")
            country["name"] = country_name
            try:
                region = data.get("claims").get("P361")[0].get("mainsnak").get("datavalue").get("value").get(
                    "id")  # P361 is the 'part of' tag
                region_name = self.get_regions(region)
                country["region"] = region_name
            except TypeError:
                country["region"] = "Unknown"
            self.country_map[country_id] = country
            return country

    def get_regions(self, id: str):
        region_data = json.loads(requests.get(WIKIDATA_PARSE + id + ".json").text)
        data = region_data.get("entities").get(id)
        region_name = data.get("labels").get("en").get("value")
        # continent_id = data.get("claims").get("P30")[0].get("mainsnak").get("datavalue").get("value").get("id")
        return region_name  # , self.continent_map.get(continent_id)

    def update_gender_map(self, key: str, value: str):
        self.gender_map.put(key, value)

    def update_maps_jsons(self):
        with open(GENDER_MAP_JSON, 'w') as f:
            json.dump(self.gender_map, f)
        with open(COUNTRY_MAP_JSON, 'w') as f:
            json.dump(self.country_map, f)
        with open(AUTHOR_MAP_JSON, 'w') as f:
            json.dump(self.author_map, f)


def main():
    data = AuthorData();
    # filename = input("Please enter a filename: ")
    filename = "goodreads/nj_goodreads_library_export.csv"
    author_data = data.read_csv(filename)
    print(author_data)
    data.write_csv(filename, author_data)


if __name__ == "__main__":
    main()
