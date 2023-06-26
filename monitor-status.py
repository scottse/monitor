#!/usr/bin/env python3
import json
import psycopg2
import csv

# Using a json file to import elements for the database connection.
db_dbname = json.loads(open('sql.json', 'r').read())['sql']['pg_dbname']
db_user = json.loads(open('sql.json', 'r').read())['sql']['pg_user']
db_pass = json.loads(open('sql.json', 'r').read())['sql']['pg_pass']
db_host = json.loads(open('sql.json', 'r').read())['sql']['pg_host']
#db_port = json.loads(open('sql.json', 'r').read())['sql']['pg_port']

# Connect to database
try:
    pg_conn = psycopg2.connect(dbname=db_dbname, user=db_user, host=db_host, password=db_pass)
except psycopg2.OperationalError:
    print('Unable to connect to database. Please check network connect or username/password.')

pg_cur = pg_conn.cursor()

# Get a list of hostnames from the database.
def nodes():
    pg_cur.execute("SELECT hostname,ip_addr,status,timestamp FROM nodes")
    db_fetch = pg_cur.fetchall()
    
    nodes_csv = open('nodes.csv', 'w')
    cw = csv.writer(nodes_csv)
    c_header = ['hostname', 'IP address', 'Status', 'Last Updated']
    cw.writerow(c_header)
    cw.writerows(db_fetch)
    
    nodes_csv.close()

# Get a list of URLs from the database.
def website():
    pg_cur.execute("SELECT url,ip_addr,status,timestamp FROM websites")
    db_fetch = pg_cur.fetchall()
    
    url_csv= open('url.csv', 'w')
    cw = csv.writer(url_csv)
    c_header = ['URL', 'IP Address', 'Status', 'Last Updated']
    cw.writerow(c_header)
    cw.writerows(db_fetch)
    
    url_csv.close()


nodes()
website()
