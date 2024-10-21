from flask import Flask, render_template, request
import requests
import socket

app = Flask(__name__)

def get_ipv4_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

ipv4 = get_ipv4_address()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showcase')
def show_case():
    keyword = request.args.get('keyword', None)

    if keyword:
        keyword = keyword.lower()
        # koyeb_url = "http://127.0.0.1:5001"
        koyeb_url = "https://quickest-gael-certscraper-2d7172a3.koyeb.app"

        try:
            response = requests.get(f'{koyeb_url}/courses?keyword={keyword}')
            response.raise_for_status()  # Raise an error for bad responses

            filtered_items = response.json()
            return render_template('showcase.html', items=filtered_items)

        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            return render_template('showcase.html', items=None)
    else:
        print("No keyword provided.")
        return render_template('showcase.html', items=None)  # Handle the case when no keyword is provided


if __name__ == '__main__':
    pass
