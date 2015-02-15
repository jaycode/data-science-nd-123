#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
"""
The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

global_prefix = "Jalan"
mapping = [ {"jl.": global_prefix},
            {"Jl.": global_prefix},
            {"jalan": global_prefix},
            {"Jalan": global_prefix}, # Repeat just in case we have concatenated names i.e. "JalanSomething"
            {"JLN.": global_prefix},
            {"JL.": global_prefix},
            {"Jln.": global_prefix},
            {"jln": global_prefix},
            {"J l .": global_prefix},
            {"J": global_prefix}]

# Street names having these matches must not be added prefix "Jalan"
outlier_regexii = [r'(?:[Ss]treet)$', r'(?:[Rr]oad)$']
remove_nextto = r'[/,-]'

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        for key in element.attrib:
            if key in CREATED:
                if "created" not in node:
                    node["created"] = {}
                node["created"][key] = element.attrib[key]
            elif key == "lon":
                if "pos" not in node:
                    node["pos"] = [0,0]
                node["pos"][0] = float(element.attrib[key])
            elif key == "lat":
                if "pos" not in node:
                    node["pos"] = [0,0]
                node["pos"][1] = float(element.attrib[key])
            else:
                node[key] = element.attrib[key]
        node["type"] = element.tag
        for child_element in iter(element):
            if child_element.tag == "tag":
                key = child_element.attrib["k"]
                in_address = False
                if key.startswith("addr:"):
                    in_address = True
                    key = key.replace("addr:", "", 1)
                if (lower.search(key) or lower_colon.search(key)) and not problemchars.search(key):
                    value = child_element.attrib["v"]
                    if in_address:
                        if "address" not in node:
                            node["address"] = {}
                        if ":" not in key:
                            if key == "street":
                                node["address"][key] = update_street_name(value, mapping)
                            else:
                                node["address"][key] = value
                    else:
                        node[key] = value
            elif child_element.tag == "nd":
                if "node_refs" not in node:
                    node["node_refs"] = []
                node["node_refs"].append(child_element.attrib["ref"])
        return node
    else:
        return None

# Uppercase first letter of each word, and do nothing else.
def upcaseplus(s):
    return " ".join([i[0].upper() + i[1:] for i in s.split()])

def update_street_name(name, mapping):
    replaced = False

    # Removes anything next to remove_nextto regex
    m = re.search(remove_nextto, name)
    if m is not None:
        name = name[0:m.start(0)].strip()
    # Replaces according to mapping, except for names matching outlier_regexii.
    for regex in outlier_regexii:
        result = re.search(regex, name)
        if result is not None:
            string = result.group(0)
            # "sunsetroad" to "sunset road "
            name = name.replace(string, " {} ".format(string))
            # "sunset road " to "Sunset Road"
            name = upcaseplus(" ".join(name.split()))
            replaced = True
    if not replaced:
        for item in mapping:
            for prefix in item:
                if name.startswith(prefix) and not replaced:
                    name = upcaseplus(name.replace(prefix, "", 1).strip())
                    name = " ".join([item[prefix], name])
                    replaced = True
                    break

    # Add the rest with global prefix
    if not replaced:
        name = "{0} {1}".format(global_prefix, upcaseplus(name))

    return name


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")

    return data

def store_data(data):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.project2
    db.openstreet.remove()
    db.openstreet.insert(data)
    db.openstreet.ensureIndex({"pos":"2dsphere"})

def test():
    data = process_map('map', True)
    pprint.pprint(data[-1])

    store_data(data)

if __name__ == "__main__":
    test()