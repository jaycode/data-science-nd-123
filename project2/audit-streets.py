import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs

OSMFILE = "map"
street_prefix_re = re.compile(r'\b\S+\.?', re.IGNORECASE)

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

def audit_street_prefix(street_prefixes, street_name):
    m = street_prefix_re.search(street_name)
    if m:
        street_prefix = m.group()
        if street_prefix not in street_prefixes:
            street_prefixes[street_prefix] = 1
        else:
            street_prefixes[street_prefix] += 1

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_prefixes = defaultdict(set)
    street_names = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_prefix(street_prefixes, tag.attrib['v'])
                    street_names.add(tag.attrib['v'])

    return street_names


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


def test():
    street_names = audit(OSMFILE)
    # pprint.pprint(street_names)
    with codecs.open("names.txt", "w") as text_file:
        text_file.write("")
    for name in street_names:
        better_name = update_street_name(name, mapping)
        try:
            with codecs.open("names.txt", "a") as text_file:
                text_file.write(name + " => " + better_name + "\n")
            # print name, " => ", better_name
        except:
            pass
        if name == "jln flamboyan2 perumnas":
            assert better_name == "Jalan Flamboyan2 Perumnas"
        if name == "Popies II / Benesari, Kuta":
            assert better_name == "Jalan Popies II"
        if name == "By Pass Sunset Road":
            assert better_name == "By Pass Sunset Road"

if __name__ == '__main__':
    test()