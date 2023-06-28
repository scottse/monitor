#!/usr/bin/env python3

import psycopg2
import json
import requests
import time
import sched
import sys
import logging
from icmplib import multiping

# Global vars
# Using a json file to import elements for the database connection.
db_dbname = json.loads(open('sql.json', 'r').read())['sql']['pg_dbname']
db_user = json.loads(open('sql.json', 'r').read())['sql']['pg_user']
db_pass = json.loads(open('sql.json', 'r').read())['sql']['pg_pass']
db_host = json.loads(open('sql.json', 'r').read())['sql']['pg_host']
#db_port = json.loads(open('sql.json', 'r').read())['sql']['pg_port']
# Date and time used for timestamp in the database.
t = time.strftime("%Y/%m/%d %H:%M:%S %Z")
# Time deplay between testing nodes and urls.
sch_delay = 300

# Test the connectivity of nodes
def ping_nodes():
    pg_cur.execute("SELECT ip_addr FROM nodes")
    fetch_from_db = pg_cur.fetchall()
    node_list = [x[0] for x in fetch_from_db]

    mp = multiping(node_list, privileged=False)
    t = time.strftime("%Y/%m/%d %H:%M:%S %Z")
    
    for p in mp:
        if p.is_alive:
            #print(f'{p.address} is up') # for debug
            # Updates the database with the status of 'up' and it also adds a timestamp.
            pg_cur.execute(f"UPDATE nodes SET status = 'up' WHERE ip_addr = '{p.address}'")
            # Updates the database with the status of 'up' and it also adds a timestamp.
            pg_cur.execute(f"UPDATE nodes SET timestamp = '{t}' WHERE ip_addr = '{p.address}'")
        else:
            #print(f'{p.address} is down') # for debug
            # Updates the database with the status of 'down' and it also adds a timestamp.
            pg_cur.execute(f"UPDATE nodes SET status = 'down' WHERE ip_addr = '{p.address}'")
            pg_cur.execute(f"UPDATE nodes SET timestamp = '{t}' WHERE ip_addr = '{p.address}'")
            
            # Error logging
            logging.warning(f'{p.address} is down')

    conn.commit()

# Check if the a website returns a HTTP status code of 200.
def url_check():
    pg_cur.execute("SELECT url FROM websites")
    fetch_from_db = pg_cur.fetchall()
    url_list = [x[0] for x in fetch_from_db]

    for i in url_list:
        try:
            r = requests.get(i)
            if r.status_code == 200:
                #print('up') # for debug
                # Updates the database with status of "up", and it also adds a timestamp.
                pg_cur.execute(f"UPDATE websites SET status = 'up' WHERE url = '{i}'")
                pg_cur.execute(f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")
            else:
                #print('down') # for debug
                # Updates the database with status of 'down', and it also adds a timestamp.
                pg_cur.execute(f"UPDATE websites SET status = 'down' WHERE url = '{i}'")
                pg_cur.execute(f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")
                
                # Error logging
                logging.warning(f'{i} did not have http status 200')
        except requests.ConnectionError:
            #print(f'connection fail on {i}') # for debug
            pg_cur.execute(f"UPDATE websites SET status = 'dns error' WHERE url = '{i}'")
            pg_cur.execute(f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")
            logging.warning(f'{i} failed to connect. DNS?')
    
    conn.commit()

def main():
    # This calls the ping_nodes() function to ping all of the nodes in the database.
    ping_nodes()
    # The url_check function is used for checking the http status code of a website. 
    url_check()

if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(filename='/opt/monitor/monitor.log',
            filemode='a',
            format='%(asctime)s, %(levelname)s %(message)s',
            level=logging.WARNING)
    
    # Test connection to database server. The program will exit if it cannot conenct to the database or 
    # if username/password is not correct.
    try:
        conn = psycopg2.connect(dbname=db_dbname, user=db_user, host=db_host, password=db_pass)
        pg_cur = conn.cursor()
    except psycopg2.OperationalError:
        logging.fatal("Unable to connect to database. Please check network connection/username/password and try again.")
        sys.exit(1)

    # The sched module is being used to schedule the tasks that runs at the speified time.
    sch = sched.scheduler(time.time, time.sleep)

    def schedule_task():
        sch.enter(sch_delay, 1, main, ())
        sch.enter(sch_delay, 1, schedule_task, ())
    
    schedule_task()
    sch.run()