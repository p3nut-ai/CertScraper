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
        koyeb_url = "https://quickest-gael-certscraper-2d7172a3.koyeb.app/"  # Ensure this is correct
        response = requests.get(f'{koyeb_url}/courses?keyword={keyword}')
        print(response)
        if response.status_code == 200:
            try:
                filtered_items = response.json()
                print(filtered_items)
                return render_template('showcase.html', items=filtered_items)
            except ValueError as e:
                print(f"Error decoding JSON: {e}")
                return render_template('showcase.html', items=None)
        elif response.status_code == 404:
            return render_template('showcase.html', items=None)
        else:
            print(f"Error: Received status code {response.status_code}")
            return render_template('showcase.html', items=None)
    else:
        print("No keyword provided.")
        return render_template('showcase.html', items=None)  # Handle the case when no keyword is provided

if __name__ == '__main__':
    # app.run(debug=True)
    # pass
