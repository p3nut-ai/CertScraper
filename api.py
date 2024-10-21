from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import pool

app = Flask(__name__)


def get_courses(keyword=None):
    # Establish a direct connection to the database
    connection = psycopg2.connect(
        host='ep-green-sound-a1uzn10c.ap-southeast-1.pg.koyeb.app',
        port='5432',
        user='koyeb-adm',
        password='Mbc1Dxzs5uiS',
        dbname='koyebdb'
    )
    try:
        cursor = connection.cursor()
        print(cursor)
        if keyword:
            keywords = [kw.strip() for kw in keyword.split(',')]
            pattern = '|'.join(keywords)
            cursor.execute("SELECT * FROM courses WHERE title ILIKE %s", (f"%{pattern}%",))
        else:
            cursor.execute("SELECT * FROM courses")

        courses = cursor.fetchall()
        print(courses)  # This will print the fetched courses
        return courses
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []
    finally:
        cursor.close()  # Close the cursor
        connection.close()  # Close the connection


@app.route('/courses', methods=['GET'])
def courses():
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

if __name__ == '__main__':
    # app.run(debug=True)
