#!/usr/bin/env python3
import json
import psycopg2
import csv
import pandas

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

    p_tables = pandas.read_csv('nodes.csv')
    p_tables.to_html('nodes.txt')
    p_html = p_tables.to_html()

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
    p_tables = pandas.read_csv('url.csv')
    p_tables.to_html('url.txt')
    p_html = p_tables.to_html()

def status_page():
    html_file = open('index.html','w')
    html_file.write('<html>\n<head>\n<link rel="stylesheet" href="style.css">\n</head>\n<body>\n<h2>Status Page</h2>\n')
    with open('nodes.txt', 'r') as f1:
        for l1 in f1:
            html_file.write(l1)
    html_file.write('<hr class="dashed">\n')
    with open('url.txt', 'r') as f2:
        for l2 in f2:
            html_file.write(l2)
    html_file.write('\n</body>\n</html>')
nodes()
website()
status_page()
