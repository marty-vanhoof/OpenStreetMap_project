## You need the corresponding csv files in order to run this script.  In order to get the csv files
## from the osm file, first run the script 'osm_to_csv.py' 

import sqlite3
import csv
from pprint import pprint

sqlite_file = 'ClaringtonPlusDB.db'

# Connect to the database
conn = sqlite3.connect(sqlite_file)

# Create a cursor object
cur = conn.cursor()


# Create the tables, specifying the column names and data types:

cur.execute('''
    CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY, lat REAL, lon REAL, user TEXT, uid INTEGER, 
    version TEXT, changeset INTEGER, timestamp DATE)
''')
conn.commit()

cur.execute('''
   CREATE TABLE IF NOT EXISTS nodes_tags(id INTEGER, key TEXT, value TEXT, type TEXT)
''')
conn.commit()

cur.execute('''
   CREATE TABLE IF NOT EXISTS ways(id INTEGER PRIMARY KEY, user TEXT, uid INTEGER, version TEXT, 
   changeset INTEGER, timestamp DATE)
''')
conn.commit()

cur.execute('''
   CREATE TABLE IF NOT EXISTS ways_tags(id INTEGER, key TEXT, value TEXT, type TEXT)
''')
conn.commit()

cur.execute('''
   CREATE TABLE IF NOT EXISTS ways_nodes(id INTEGER, node_id INTEGER, position INTEGER)
''')
conn.commit()


# Read in the csv files as dictionaries, format the data as a list of tuples:

with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db1 = [(i['id'],i['lat'],i['lon'],i['user'],i['uid'],i['version'],i['changeset'],i['timestamp']) for i in dr]

with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db2 = [(i['id'], i['key'],i['value'], i['type']) for i in dr]
    
with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db3 = [(i['id'], i['user'],i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]
    
with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db4 = [(i['id'], i['key'], i['value'].decode("utf-8"), i['type']) for i in dr]
    
with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db5 = [(i['id'], i['node_id'], i['position']) for i in dr]


# insert the formatted data

#cur.executemany("INSERT INTO nodes(id,lat,lon,user,uid,version,changeset,timestamp) VALUES (?,?,?,?,?,?,?,?);", to_db1)

#cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db2)

#cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db3)

#cur.executemany("INSERT INTO ways_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db4)

#cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db5)


# commit the changes

conn.commit()

cur.execute('SELECT * FROM ways_nodes limit 500')
rows = cur.fetchall()
print('1):')
pprint(rows)

conn.close()