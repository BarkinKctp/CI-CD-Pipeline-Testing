from flask import Flask, render_template
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='/static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<random_string>')
def return_backwards_string(random_string):
    reversed_text = "".join(reversed(random_string))
    return render_template('reverse.html', input_text=random_string, reversed_text=reversed_text)

@app.route('/api/reverse/<random_string>')
def reverse_string_api(random_string):
    return "".join(reversed(random_string))

@app.route('/get-mode')
def get_mode():
    mode_value = os.environ.get("MODE", "No mode set")
    return render_template('mode.html', mode_value=mode_value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)