#!/usr/bin/env python3
# Add new items to monitor.
import psycopg2
import json
import sys
import argparse

# Access to json file to provide database connection details.
db_dbname = json.loads(open('sql.json', 'r').read())['sql']['pg_dbname']
db_user = json.loads(open('sql.json', 'r').read())['sql']['pg_user']
db_pass = json.loads(open('sql.json', 'r').read())['sql']['pg_pass']
db_host = json.loads(open('sql.json', 'r').read())['sql']['pg_host']

# Connect to database
try:
    pg_conn = psycopg2.connect(
        dbname=db_dbname, user=db_user, host=db_host, password=db_pass)
    pg_cur = pg_conn.cursor()
except psycopg2.OperationalError:
    print('Unable to connect to database. Please check network connect or username/password.')

# Get a list of hostnames from the database.


def h_list():
    pg_cur.execute("SELECT hostname FROM nodes")

    db_fetch = pg_cur.fetchall()

    node_list = [x[0] for x in db_fetch]

    return node_list

# Get a list of IP addresses from the database.


def i_list():
    pg_cur.execute("SELECT ip_addr FROM nodes")

    db_fetch = pg_cur.fetchall()

    ip_list = [x[0] for x in db_fetch]

    return ip_list

# Get a list of URLs from the database.


def u_list():
    pg_cur.execute("SELECT url FROM websites")

    db_fetch = pg_cur.fetchall()

    url_list = [x[0] for x in db_fetch]

    return url_list

# A function to add a host into the database.


def addhost():
    print('Please enter hostname and IP address:')

    host = input('Hostname: ')
    ip_a = input('IP: ')

    host_if = True if host in h_list() else False
    ip_if = True if ip_a in i_list() else False

    # print(host_if)
    # print(ip_if)

    if host_if or ip_if == True:
        print('Hostname or IP address already exists. Please try again.')
    else:
        pg_cur.execute(
            f"INSERT INTO nodes(hostname, ip_addr) VALUES('{host}','{ip_a}')")

    pg_conn.commit()
    pg_conn.close()

# A function to add a URL to the database.


def addweb():
    print('Please enter url: ')
    url = input('URL: ')

    url_if = True if url in u_list() else False

    if url_if == True:
        print('Hostname or IP address already exists. Please try again.')
    else:
        pg_cur.execute(f"INSERT INTO websites(url) VALUES('{url}')")

    pg_conn.commit()
    pg_conn.close()

# Using Argparse for a basic CLI for this program.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', dest='host', action='store_const', const=True)
    parser.add_argument('-web', dest='web', action='store_const', const=True)

    args = parser.parse_args()

    if args.host:
        addhost()
    elif args.web:
        addweb()
    else:
        sys.exit(print(
            'No options provided. Please add -host for adding a hostname or -web to add URL to the database.'))


if __name__ == '__main__':
    main()
