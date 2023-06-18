#!/usr/bin/env python3

import psycopg2
import json
import requests
import time
import sched
import sys
from icmplib import multiping

# Global vars
db_pass = json.loads(open('sql.json', 'r').read())['sql']['pg_pass']
t = time.strftime("%Y/%m/%d %H:%M:%S %Z")
sch_delay = 10

# Test the connectivity of nodes
def ping_nodes():  
    pg_cur.execute("SELECT ip_addr FROM nodes")
    fetch_from_db = pg_cur.fetchall()
    node_list = [x[0] for x in fetch_from_db]

    mp = multiping(node_list, privileged=False)
    t = time.strftime("%Y/%m/%d %H:%M:%S %Z")
    
    for p in mp:
        if p.is_alive:
            print(f'{p.address} is up')
            pg_cur.execute(f"UPDATE nodes SET status = 'up' WHERE ip_addr = '{p.address}'")
            pg_cur.execute(f"UPDATE nodes SET timestamp = '{t}' WHERE ip_addr = '{p.address}'")
        else:
            print(f'{p.address} is down')
            pg_cur.execute(f"UPDATE nodes SET status = 'down' WHERE ip_addr = '{p.address}'")
            pg_cur.execute(f"UPDATE nodes SET timestamp = '{t}' WHERE ip_addr = '{p.address}'")

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
                print('up')
                pg_cur.execute(f"UPDATE websites SET status = 'up' WHERE url = '{i}'")
                pg_cur.execute(f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")
            else:
                print('down')
                pg_cur.execute(f"UPDATE websites SET status = 'down' WHERE url = '{i}'")
                pg_cur.execute(f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")
        except requests.ConnectionError:
            print(f'connection fail on {i}')
            pg_cur.execute(f"UPDATE websites SET status = 'dns error' WHERE url = '{i}'")
            pg_cur.execute(f"UPDATE websites SET timestamp = '{t}' WHERE url = '{i}'")
    
    conn.commit()

def main():
    # This calls the ping_nodes() function to ping all of the nodes in the database.
    ping_nodes()
    # The url_check function is used for checking the http status code of a website. 
    url_check()

if __name__ == "__main__":
    # Test connection to database server. The program will exit if it cannot conenct to the database or 
    # if username/password is not correct.
    try:
        conn = psycopg2.connect(dbname='monitor', user='sqluser', host='192.168.64.14', password='test')
        pg_cur = conn.cursor()
    except psycopg2.OperationalError:
        sys.exit("Failed to connect to DB. Please check if the network connection or username/password is correct.")
    
    # The sched module is being used to schedule the tasks that runs at the speified time.
    sch = sched.scheduler(time.time, time.sleep)

    def schedule_task():
        sch.enter(sch_delay, 1, main, ())
        sch.enter(sch_delay, 1, schedule_task, ())
    
    schedule_task()
    sch.run()