from flask import Flask, render_template, request,jsonify,abort
import requests
import socket
import psycopg2
from psycopg2 import pool
import time
import re

app = Flask(__name__)


# Set to store unique IP addresses
unique_ips = set()

# Limit the number of unique IPs allowed
IP_LIMIT = 200

@app.before_request
def limit_ips():
    user_ip = request.remote_addr
    visitor_count = 0
    print(f"Current unique IPs: {unique_ips}")
    if user_ip not in unique_ips:
        if len(unique_ips) < IP_LIMIT:
            unique_ips.add(user_ip)  # Add the IP if under limit
            visitor_count += 1
            print(f"Visitor count: {visitor_count}")
        else:
            abort(403)  # Block access once limit is reached

# print(unique_ips)

def get_ipv4_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

ipv4 = get_ipv4_address()

@app.route('/')
def index():
    return render_template('landpage.html')

@app.route('/homepage')
def homepage():
    return render_template('index.html')

@app.route('/showcase')
def show_case():
    keyword = request.args.get('keyword', None)
    courses_data = get_courses(keyword)  # Fetch from the database directly

    if courses_data:
        formatted_courses = [
            {
                "id": course[0],
                "title": course[1],
                "link": course[2],
                "description": course[3],
                "thumbnail_url": course[4],
                "created_at": course[5],
                "expiration_date": course[6]
            }
            for course in courses_data
        ]
        return render_template('showcase.html', items=formatted_courses)
    else:
        print("No courses found.")
        return render_template('showcase.html', items=None) # Handle the case when no keyword is provided


db_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections
    10,  # Maximum number of connections
    user='koyeb-adm',
    password='Mbc1Dxzs5uiS',
    host='ep-green-sound-a1uzn10c.ap-southeast-1.pg.koyeb.app',
    port='5432',
    database='koyebdb'
)

def get_courses(keyword=None):
    connection = None
    cursor = None
    try:
        connection = db_pool.getconn()  # Get connection from pool
        cursor = connection.cursor()
        print(f"Connected to database, cursor: {cursor}")

        if keyword:
            # Processing keywords for regex
            keywords = [kw.strip() for kw in keyword.split(',')]
            # Create a regex pattern with case-insensitive flag
            pattern = '|'.join(map(re.escape, keywords))  # Escape any special regex characters
            regex_query = f"title ~* %s"  # The ~* operator is for case-insensitive regex matching
            cursor.execute(f"SELECT * FROM courses WHERE {regex_query}", (pattern,))
        else:
            cursor.execute("SELECT * FROM courses")

        courses = cursor.fetchall()
        print(f"Fetched courses: {courses}")
        return courses
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            db_pool.putconn(connection)  # Return connection to pool

@app.route('/courses')
def courses():
    # print(f"Received request for courses with keyword: {request.args.get('keyword', None)}")
    keyword = request.args.get('keyword', None)
    courses_data = get_courses(keyword)

    if courses_data:
        formatted_courses = [
            {
                "id": course[0],
                "title": course[1],
                "link": course[2],
                "description": course[3],
                "thumbnail_url": course[4],
                "created_at": course[5],
                "expiration_date": course[6]
            }
            for course in courses_data
        ]
        return jsonify(formatted_courses)
    else:
        return jsonify({"error": "No courses found."}), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403


if __name__ == '__main__':
    pass
