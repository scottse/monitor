#!/usr/bin/env python3
import json
import psycopg2
import csv
import pandas

# Using a json file to import elements for the database connection.
db_dbname = json.loads(open('database.json', 'r').read())['sql']['pg_dbname']
db_user = json.loads(open('database.json', 'r').read())['sql']['pg_user']
db_pass = json.loads(open('database.json', 'r').read())['sql']['pg_pass']
db_host = json.loads(open('database.json', 'r').read())['sql']['pg_host']
#db_port = json.loads(open('database.json', 'r').read())['sql']['pg_port']

# Connect to database
try:
    pg_conn = psycopg2.connect(dbname=db_dbname, user=db_user, host=db_host, password=db_pass)
except psycopg2.OperationalError:
    print('Unable to connect to database. Please check network connect or username/password.')

pg_cur = pg_conn.cursor()

# Gets node data from the monitor database.
def nodes_table():
    pg_cur.execute("SELECT hostname,ip_addr,status,timestamp FROM nodes")
    db_fetch = pg_cur.fetchall()
    
    # Creates the csv file.
    nodes_csv = open('webpage/nodes.csv', 'w')
    cw = csv.writer(nodes_csv)
    c_header = ['hostname', 'IP address', 'Status', 'Last Updated']
    cw.writerow(c_header)
    cw.writerows(db_fetch)
    nodes_csv.close()
    
    # Creates text file of html data from the csv.
    p_tables = pandas.read_csv('webpage/nodes.csv')
    p_tables.to_html('webpage/nodes.txt', index=False)
    p_html = p_tables.to_html()

# Get data related to URLs from the monitor database.
def website_table():
    pg_cur.execute("SELECT url,ip_addr,status,timestamp FROM websites")
    db_fetch = pg_cur.fetchall()
    
    # Creates text file of html data from the csv.
    url_csv= open('webpage/url.csv', 'w')
    cw = csv.writer(url_csv)
    c_header = ['URL', 'IP Address', 'Status', 'Last Updated']
    cw.writerow(c_header)
    cw.writerows(db_fetch)
    url_csv.close()

    # Creates text file of html data from the csv.
    p_tables = pandas.read_csv('webpage/url.csv')
    p_tables.to_html('webpage/url.txt', index=False)
    p_html = p_tables.to_html()

# Creates a web page with the status of each item being monitor from the database.
def status_webpage():
    # Creates the index.html file by writing the html code into it. It pulls the html table code
    # from texts files created from the nodes and website
    html_file = open('webpage/index.html','w')
    html_file.write(
        '<html>\n<head>\n<link rel="stylesheet" href="style.css">\n</head>\n<body>\n<h2>Project Monitor Status Page</h2>\n'
        )
    html_file.writelines('<h3>Nodes:</h3>')
    with open('nodes.txt', 'r') as f1:
        for l1 in f1:
            html_file.write(l1)
    html_file.write('<hr class="dashed">\n')
    html_file.writelines('<h3>Websites:</h3>')
    with open('url.txt', 'r') as f2:
        for l2 in f2:
            html_file.write(l2)
    html_file.write('\n</body>\n</html>')

def main():
    nodes_table()
    website_table()
    status_webpage()


if __name__ == '__main__':
    main()