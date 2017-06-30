import sqlite3
from pprint import pprint

database_file = 'ClaringtonPlusDB.db'
conn = sqlite3.connect(database_file)
cursor = conn.cursor()


# These are all the functions I wrote to query the 'ClaringtonPlusDB.db' database


def postal_code_counts():
    query = "select subq.value, count(*) as count \
            from (select * from nodes_tags union select * from ways_tags) subq \
            where subq.key = 'postcode' group by subq.value order by count desc"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)
    

def pragma(command):
    query = "pragma {}".format(command)
    cursor.execute(query)
    results = cursor.fetchall()
    return results

    
#page_size = float(pragma('page_size')[0][0])
#page_count = float(pragma('page_count')[0][0])
#file_size_mb = (page_size * page_count) / 10**6
#print file_size_mb


def user_count():
    query = "select count(sub.uid) from \
        (select uid from nodes union select uid from ways) sub"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)

    
def nodes_count():
    query = "select count(*) from nodes"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)


def ways_count():
    query = "select count(*) from ways"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)
    
    
def get_places():
    query = "select sub.value, nt.value from nodes_tags nt join \
            (select id, value from nodes_tags where key = 'place') sub \
            on nt.id = sub.id where nt.key = 'name' limit 10"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)
    

def place_count():
    query = "select value, count(*) from nodes_tags where key = 'place' group by value"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)
    
    
def amenities_count():
    query = "select value, count(*) as num from nodes_tags where key = 'amenity' group by value \
            order by num desc limit 10"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)
    
    
def pizza_restaurants():
    query = "select nt.value, count(*) as count from nodes_tags nt join \
            (select id, value from nodes_tags where value = 'pizza') sub \
            on nt.id = sub.id where nt.key = 'name' group by nt.value order by count desc"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)
    

def top_users():
    query = "select sub.uid, sub.user, count(*) as count from \
        (select uid, user from nodes union all select uid, user from ways) sub \
        group by sub.uid order by count desc limit 10"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)


def get_phone_numbers():
    query = "select sub.value from \
            (select key, value from nodes_tags union select key, value from ways_tags) sub \
            where sub.key = 'phone'"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)
    
    
def postal_code_counts():
    query = "select subq.value, count(*) as count \
            from (select * from nodes_tags union select * from ways_tags) subq \
            where subq.key = 'postcode' group by subq.value order by count desc"
    cursor.execute(query)
    results = cursor.fetchall()
    pprint(results)
    
    
conn.close()