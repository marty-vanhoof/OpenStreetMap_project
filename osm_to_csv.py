import csv
import codecs
import xml.etree.cElementTree as ET
import cerberus
import schema
import re

from pprint import pprint
from auditing_cleaning import is_street_name
from auditing_cleaning import is_postal_code
from auditing_cleaning import is_city
from auditing_cleaning import update_street_name
from auditing_cleaning import update_postal_code
from auditing_cleaning import update_city

mapping = { "Ave": "Avenue",
            "Ave." : "Avenue",
            "Cres" : "Crescent",
            "Ct" : "Court",
            "Dr" : "Drive",
            "Rd" : "Road",
            "St": "Street"}

mapping2 = {"Rd E" : "Road East", "St E" : "Street East", "St N" : "Street North", "Blvd N" : "Boulevard North"}

    
## Preparing for the Database    
    

OSM_PATH = "ClaringtonPlus.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+\/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']



# The function 'make_tag_dict()' takes an element and a child tag, and then creates a dictionary with keys 'id', 'key', 'value', 'type'
# according to the rules specified in the problem

def make_tag_dict(element, tag):
    tag_attribs = {}                           
    tag_attribs['id'] = element.attrib['id']
    
    if is_street_name(tag):
        tag_attribs['value'] = update_street_name(tag.attrib['v'], mapping, mapping2)  
    elif is_postal_code(tag):
        tag_attribs['value'] = update_postal_code(tag.attrib['v'])              # update street names, postal codes,
    elif is_city(tag):                                                          # and city names using the respective
        tag_attribs['value'] = update_city(tag.attrib['v'])                     # functions 
    else:
        tag_attribs['value'] = tag.attrib['v']
    
    k_attrib = tag.attrib['k']
    if not PROBLEMCHARS.search(k_attrib):
        if LOWER_COLON.search(k_attrib):        # If the 'k_attrib' string contains a ':' character, then set 
            key = k_attrib.split(':', 1)[1]     # tag_attribs['key'] to be everything after the first colon,
            tipe = k_attrib.split(':', 1)[0]    # and tag_attribs['type'] to be everything before the first colon
            tag_attribs['key'] = key
            tag_attribs['type'] = tipe
        else:
            tag_attribs['key'] = k_attrib
            tag_attribs['type'] = 'regular'
        
    return tag_attribs


def shape_element(element):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for item in NODE_FIELDS:                      # Populate the 'node_attribs' dict with the keys from NODE_FIELDS
            node_attribs[item] = element.attrib[item] # and the values from the 'element.attrib' dictionary
        for tag in element.iter('tag'):
            if tag.attrib['v'] == "" or tag.attrib['v'] == None:
                continue
            tag_attribs = make_tag_dict(element, tag) # Call the function make_tag_dict() that creates a dictionary of
            tags.append(tag_attribs)                  # tag attributes.  Then append this dict to the 'tags' list.
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for item in WAY_FIELDS:                       # Populate the 'way_attribs' dict with the keys from WAY_FIELDS
            way_attribs[item] = element.attrib[item]  # and the values from the 'element.attrib' dict
        for tag in element.iter('tag'):
            if tag.attrib['v'] == "" or tag.attrib['v'] == None:
                continue
            tag_attribs = make_tag_dict(element, tag) # Again use the function make_tag_dict() to create a dictionary 
            tags.append(tag_attribs)                  # of tag attributes
            
        position = 0
        for tag in element.iter('nd'):
            nd_attribs = {}                           # Initialize and populate the 'nd_attribs' dictionary according
            nd_attribs['id'] = element.attrib['id']   # to the rules specified in the problem
            nd_attribs['node_id'] = tag.attrib['ref']
            nd_attribs['position'] = position
            position += 1
            way_nodes.append(nd_attribs)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    

# ================================================== #
#              Other Helper Functions                #
# ================================================== #


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #


def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

