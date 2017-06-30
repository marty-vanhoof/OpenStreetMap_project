import xml.etree.cElementTree as ET
from pprint import pprint
from collections import defaultdict
import re

# the OSM file needs to be downloaded locally.  If the filename changes, then
# the name should be changed here as well
osm_file = 'ClaringtonPlus.osm'

# python regular expression object that captures the last word of a string
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


##  AUDITING FUNCTIONS - These functions are for auditing osm_file


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", "Path", "Loop", 
            "Trail", "Parkway", "Commons", "Circle", "Crescent", "Gate", "Greenway", "Heights", "Line", "Terrace",
            "Way", "North", "South", "West", "East", "Champions", "Clarke", "Driver", "Freeway"]

            
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    return street_types


def audit_postal_code(postal_code_types, postal_code):  
    if not postal_code.isupper() or ' ' not in postal_code:
        postal_code_types['case_whitespace_problems'].add(postal_code)
    else:
        postal_code_types['other'].add(postal_code)
    return postal_code_types
    

def audit_city(cities, city):
    cities.add(city)
    return cities
    

def is_street_name(element):
    return (element.attrib['k'] == "addr:street")


def is_postal_code(element):
    return (element.attrib['k'] == "addr:postcode")


def is_city(element):
    return (element.attrib['k'] == "addr:city")


# This function 'audit()' will use the specific auditing functions defined above to check 
# for problems with street names, postal codes, or city names and store them in different 
# data structures.  The function returns a 3-tuple:  The first element of the tuple is a 
# dictionary of audited street types, the second element is a dictionary of audited postal 
# codes, and the third element is a set of audited city names.


def audit(filename):
    f = open(filename, "r")
    street_types = defaultdict(set)
    postal_code_types = defaultdict(set)
    cities = set()
    
    for event, element in ET.iterparse(f, events=("start",)):
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_postal_code(tag):
                    audit_postal_code(postal_code_types, tag.attrib['v'])
                if is_city(tag):
                    audit_city(cities, tag.attrib['v'])
    
    f.close()
    return dict(street_types), dict(postal_code_types), cities
    
    
## CLEANING FUNCTIONS - These functions are for cleaning osm_file


mapping = { "Ave": "Avenue",
            "Ave." : "Avenue",
            "Cres" : "Crescent",
            "Ct" : "Court",
            "Dr" : "Drive",
            "Rd" : "Road",
            "St": "Street"}

mapping2 = {"Rd E" : "Road East", "St E" : "Street East", "St N" : "Street North", "Blvd N" : "Boulevard North"}


def update_street_name(street_name, mapping, mapping2):
    street_name = street_name.replace('  ', ' ')
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        double_street_type = ' '.join(street_name.split()[-2:])
        if street_type in mapping.keys():
            street_name = re.sub(street_type, mapping[street_type], street_name)
        if double_street_type in mapping2.keys():
            street_name = re.sub(double_street_type, mapping2[double_street_type], street_name)

    return street_name


def update_postal_code(postal_code): 
    postal_code = postal_code.upper()
    if ' ' not in postal_code:
        if len(postal_code) == 6:
            postal_code = postal_code[0:3]+' '+postal_code[3:6]
            
    return postal_code
    

def update_city(city):
    if city == 'Bowmanwille':
        city = city.replace('nw', 'nv')
    if city == 'City of Oshawa':
        city = 'Oshawa'
    if city in ['Town of Whitby', 'whitby']:
        city = 'Whitby'
    
    return city


def street_test():
    st_types = audit(osm_file)[0]
    #pprint(st_types)
    print ""

    for st_type, st_names in st_types.iteritems():
        for name in st_names:
            better_name = update_street_name(name, mapping, mapping2)
            print name, "=>", better_name
            
            
def postal_code_test():
    postcode_types = audit(osm_file)[1]
    #pprint(postcode_types)
    print ""
    
    for postcode_type, postcodes in postcode_types.iteritems():
        for postcode in postcodes:
            better_postcode = update_postal_code(postcode)
            print postcode, "=>", better_postcode
            
            
def cities_test():
    CITIES = audit(osm_file)[2]
    #pprint(CITIES)
    print ""
    for city in CITIES:
        better_city = update_city(city)
        print city, "=>", better_city
            