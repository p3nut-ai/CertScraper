import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from datetime import datetime, timedelta
import psycopg2

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

base_url = 'https://coursefolder.net/category/IT-and-Software'

def setup_database():
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            host='',
            port='',
            user='',
            password='',
            dbname=''
        )
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                title TEXT,
                link TEXT,
                description TEXT,
                thumbnail_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiration_date TIMESTAMP
            )
        ''')
        connection.commit()  # Commit the changes to the database
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"The error '{e}' occurred during setup.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



def delete_old_courses(conn):
    threshold_date = datetime.now() - timedelta(days=2)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM courses WHERE created_at < %s", (threshold_date,))
    conn.commit()  # Commit the changes after the delete operation


def scrape_course_details(course_link):
    response = requests.get(course_link, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        course_details = {}
        course_includes = soup.find('div', class_='content')

        if course_includes:
            udemy_link = course_includes.find('a', class_='edu-btn')
            course_details['link'] = udemy_link['href'] if udemy_link else "N/A"
            # Directly store the course details without checking availability
            # course_details['link'] = course_link  # Keep the course link
            course_details['title'] = soup.find('h1').text.strip() if soup.find('h1') else "No title available"
            course_details['description'] = soup.find('p').get_text(strip=True) if soup.find('p') else "No description available"

            # Fetch thumbnail URL
            thumbnail_url_element = soup.find('div', class_='thumbnail').find('img')
            course_details['thumbnail_url'] = thumbnail_url_element['src'].strip() if thumbnail_url_element else "No thumbnail available"

        return course_details
    else:
        print(f"Failed to retrieve course details from: {course_link}. Status code: {response.status_code}")
        return None

def scrape_page(page_number, conn):
    url = f'{base_url}/{page_number}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        courses = soup.find_all('div', class_='edu-course')

        if not courses:
            return False

        for course in courses:
            try:
                title_element = course.find('h6', class_='title').find('a')
                course_title = title_element.text.strip().lower()
                course_link = title_element['href']

                course_details = scrape_course_details(course_link)
                # print(course_details['link'])
                # print(f"Course details for {course_title}: {course_details}")

                if not course_details or 'link' not in course_details or 'description' not in course_details or 'thumbnail_url' not in course_details:
                    print(f"Failed to retrieve complete details for: {course_title}")
                    continue

                cursor = conn.cursor()
                cursor.execute('SELECT * FROM courses WHERE link = %s', (course_details['link'],))
                existing_course = cursor.fetchone()

                if existing_course:
                    print(f"Course already exists: {course_title}")
                else:
                    try:
                        cursor.execute('''
                            INSERT INTO courses (title, link, description, thumbnail_url)
                            VALUES (%s, %s, %s, %s)
                        ''', (course_title, course_details['link'], course_details['description'], course_details['thumbnail_url']))
                        conn.commit()
                        print(f"New course inserted: {course_title}")
                    except Exception as e:
                        print(f"Error inserting course: {e}")
                        conn.rollback()  # Rollback on error

            except Exception as e:
                print(f"Error processing course: {e}")

        return True
    else:
        print(f"Failed to retrieve the page: {url}. Status code: {response.status_code}")
        return False


def main():
    connection = None
    try:
        # Setup the database (create the table if it doesn't exist)
        setup_database()

        # Connect to the database
        connection = psycopg2.connect(
            host='ep-green-sound-a1uzn10c.ap-southeast-1.pg.koyeb.app',
            port='5432',
            user='koyeb-adm',
            password='Mbc1Dxzs5uiS',
            dbname='koyebdb'
        )

        # page_number = 1  # Replace with your desired page number
        for page in range(1,13):
            scrape_page(page, connection)  # Scrape and insert data into the database
        # courses = get_courses()  # Fetching courses, make sure to pass connection if needed
        # print(f"Courses fetched: {courses}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if connection:
            connection.close()

def reset_database():
    try:
        connection = psycopg2.connect(
            host='ep-green-sound-a1uzn10c.ap-southeast-1.pg.koyeb.app',
            port='5432',
            user='koyeb-adm',
            password='Mbc1Dxzs5uiS',
            dbname='koyebdb'
        )
        cursor = connection.cursor()

        # Truncate the table
        cursor.execute("TRUNCATE TABLE courses RESTART IDENTITY CASCADE;")
        connection.commit()

        print("Database reset successfully.")

    except Exception as e:
        print(f"Error resetting database: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# def main():
#     with setup_database() as conn:
#         delete_old_courses(conn)
#         for i in range(1, 100):
#             scrape_page(i, conn)

if __name__ == "__main__":
    # reset_database()
    main()
