#!/usr/bin/env python3

import psycopg2
import json
import requests
import time
import sched
import sys
import logging
import pandas
import csv
from icmplib import multiping

# Global vars
# Using a json file to import elements for the database connection.
db_dbname = json.loads(open('database.json', 'r').read())['sql']['pg_dbname']
db_user = json.loads(open('database.json', 'r').read())['sql']['pg_user']
db_pass = json.loads(open('database.json', 'r').read())['sql']['pg_pass']
db_host = json.loads(open('database.json', 'r').read())['sql']['pg_host']
# db_port = json.loads(open('database.json', 'r').read())['sql']['pg_port']

# Date and time used for timestamp in the database.
# t = time.strftime("%Y/%m/%d %H:%M:%S %Z")
# Time delay between testing nodes and urls.
sch_delay = 300

# Working directory
work_dir = ''

# Test the connectivity of nodes
def ping_nodes():
    pg_cur.execute("SELECT ip_addr FROM nodes")
    fetch_from_db = pg_cur.fetchall()
    node_list = [x[0] for x in fetch_from_db]

    mp = multiping(node_list, privileged=False)
    t = time.strftime("%Y/%m/%d %H:%M:%S %Z")

    for p in mp:
        if p.is_alive:
            # print(f'{p.address} is up') # for debug
            # Updates the database with the status of 'up' and it also adds a timestamp.
            pg_cur.execute(
                f"UPDATE nodes SET status = 'up' WHERE ip_addr = '{p.address}'")
            # Updates the database with the status of 'up' and it also adds a timestamp.
            pg_cur.execute(
                f"UPDATE nodes SET timestamp = '{t}' WHERE ip_addr = '{p.address}'")
        else:
            # print(f'{p.address} is down') # for debug
            # Updates the database with the status of 'down' and it also adds a timestamp.
            pg_cur.execute(
                f"UPDATE nodes SET status = 'down' WHERE ip_addr = '{p.address}'")
            pg_cur.execute(
                f"UPDATE nodes SET timestamp = '{t}' WHERE ip_addr = '{p.address}'")

            # Error logging
            logging.warning(f'{p.address} is down')

    conn.commit()

# Check if the a website returns a HTTP status code of 200.
def url_check():
    pg_cur.execute("SELECT url FROM websites")
    fetch_from_db = pg_cur.fetchall()
    url_list = [x[0] for x in fetch_from_db]
    t = time.strftime("%Y/%m/%d %H:%M:%S %Z")
    
    for i in url_list:
        try:
            r = requests.get(i)
            if r.status_code == 200:
                # print('up') # for debug
                # Updates the database with status of "up", and it also adds a timestamp.
                pg_cur.execute(
                    f"UPDATE websites SET status = 'up' WHERE url = '{i}'")
                pg_cur.execute(
                    f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")
            else:
                # print('down') # for debug
                # Updates the database with status of 'down', and it also adds a timestamp.
                pg_cur.execute(
                    f"UPDATE websites SET status = 'down' WHERE url = '{i}'")
                pg_cur.execute(
                    f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")

                # Error logging
                logging.warning(f'{i} did not have http status 200')
                
        except requests.ConnectionError:
            # print(f'connection fail on {i}') # for debug
            pg_cur.execute(
                f"UPDATE websites SET status = 'dns error' WHERE url = '{i}'")
            pg_cur.execute(
                f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")
            
            #Error logging
            logging.warning(f'{i} failed to connect. DNS?')

    conn.commit()

# Prepares the nodes list with a csv file.
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
    url_csv = open('webpage/url.csv', 'w')
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
    html_file = open('/var/www/monitor/index.html', 'w')
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
    html_file.write(f'\nLast Updated: {time.strftime("%Y/%m/%d %H:%M:%S %Z")}')
    html_file.write('\n</body>\n</html>')

def main():
    # This calls the ping_nodes() function to ping all of the nodes in the database.
    ping_nodes()
    # The url_check function is used for checking the http status code of a website.
    url_check()
    # Gets the node data from the database and stores the data as a csv file.
    nodes_table()
    # Gets the website data from the database and stores the data as a csv file.
    website_table()
    # Takes the data stored in the csv files and writes index.html on each update.
    status_webpage()

if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(filename='/opt/monitor/monitor.log',
                        filemode='a',
                        format='%(asctime)s, %(levelname)s %(message)s',
                        level=logging.WARNING)

    # Test connection to database server. The program will exit if it cannot conenct to the database or
    # if username/password is not correct.
    try:
        conn = psycopg2.connect(
            dbname=db_dbname, user=db_user, host=db_host, password=db_pass)
        pg_cur = conn.cursor()
    except psycopg2.OperationalError:
        logging.fatal(
            "Unable to connect to database. Please check network connection/username/password and try again.")
        sys.exit(1)

    # The sched module is being used to schedule the tasks that runs at the speified time.
    sch = sched.scheduler(time.time, time.sleep)

    def schedule_task():
        sch.enter(sch_delay, 1, main, ())
        sch.enter(sch_delay, 1, schedule_task, ())

    schedule_task()
    sch.run()
