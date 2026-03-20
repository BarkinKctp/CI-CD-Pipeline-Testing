from flask import Flask
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

app = Flask(__name__)

CSS = """
* {
    box-sizing: border-box;
}
html,body {
    height: 100%;
}

body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #e6edf3;

    display: flex;
    flex-direction: column;
    min-height: 100vh;

    background:
        radial-gradient(900px 600px at 10% 10%, rgba(255, 255, 255, .08), transparent 60%),
        radial-gradient(700px 500px at 90% 20%, rgba(255, 255, 255, .06), transparent 55%),
        linear-gradient(180deg, #0d1117, #0b1220);

    opacity: 0;
    animation: pageIn .6s ease forwards;
}

/* ---------- Layout ---------- */

.page-content {
    max-width: 780px;
    margin: auto;
    padding: 60px 20px;
    width: 100%;
    flex: 1;
}

/* ---------- Glass Card ---------- */

.box {
    background: rgba(255, 255, 255, .05);
    border: 1px solid rgba(255, 255, 255, .12);
    border-radius: 16px;
    backdrop-filter: blur(10px);
    box-shadow: 0 18px 50px rgba(0, 0, 0, .55);
    padding: 16px;
    margin-bottom: 16px;

    transition: transform .18s ease,
        border-color .18s ease,
        box-shadow .18s ease;
}

.box:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, .22);
}

/* ---------- Typography ---------- */

.headline {
    font-size: 2.6rem;
    text-align: center;
    margin-top: 0;
    background: linear-gradient(180deg, #fff, rgba(255, 255, 255, .6));
    -webkit-background-clip: text;
    color: transparent;
}

.subheadline {
    text-align: center;
    color: #f6f7f7;
}

/* ---------- Form ---------- */

.form-row {
    display: flex;
    gap: 10px;
}

.form-row input {
    flex: 1;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, .15);
    background: #0d1117;
    color: white;
    outline: none;
    transition: .15s;
}

.form-row input:focus {
    border-color: rgba(255, 255, 255, .3);
    box-shadow: 0 0 0 4px rgba(255, 255, 255, .06);
    transform: translateY(-1px);
}

/* Apple-like button */
.form-row button {
    padding: 12px 18px;
    border-radius: 12px;
    border: none;
    font-weight: 600;
    cursor: pointer;

    background: linear-gradient(180deg, #ffffff, #cfcfcf);
    color: #0d1117;

    box-shadow: 0 10px 25px rgba(0, 0, 0, .4);
    transition: .15s;
}

.form-row button:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 40px rgba(0, 0, 0, .5);
}

.form-row button:active {
    transform: translateY(0);
}

/* ---------- Result ---------- */

.result-box {
    background: rgba(0, 0, 0, .2);
}

/* ---------- Links ---------- */

.helper {
    color: #d7dde4;
}

.helper a {
    color: #e6edf3;
    text-decoration: none;
    border-bottom: 1px solid rgba(255, 255, 255, .2);
    font-size: 1.2rem;
    font-weight: 400;
    padding: 2px 4px;
    display: inline-block;
}

.helper a:hover {
    border-bottom-color: white;
}

/* ---------- Animation ---------- */

@keyframes pageIn {
    from {
        opacity: 0;
        transform: translateY(10px);
        filter: blur(6px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
        filter: blur(0);
    }
}

/* ---------- Mobile ---------- */

@media (max-width:700px) {
    .form-row {
        flex-direction: column;
    }
}
"""

def page(title, body_content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{CSS}</style>
</head>
<body>
    <main class="page-content">
        {body_content}
    </main>
</body>
</html>"""

@app.route('/')
def home():
    return page("Flask App Home", """
        <h1 class="headline box">Welcome to the Flask App</h1>
        <p class="subheadline box">This is a small demo application to test CI/CD pipelines.</p>

        <div class="form-row box">
            <input id="inputText" type="text" placeholder="Enter text (example: Testing123)">
            <button id="reverseBtn" type="button">Reverse</button>
        </div>

        <div class="result-box box">
            <p><strong>Input:</strong> <span id="inputValue">-</span></p>
            <p><strong>Reversed:</strong> <span id="outputValue">-</span></p>
        </div>

        <p class="helper box">Direct URL test: <a href="/hello">/hello</a> returns <strong>olleh</strong></p>
        <p class="helper box">Environment check: <a href="/get-mode">/get-mode</a></p>

        <script>
            const input = document.getElementById('inputText');
            const button = document.getElementById('reverseBtn');
            const inputValue = document.getElementById('inputValue');
            const outputValue = document.getElementById('outputValue');

            async function runReverseTest() {
                const value = input.value.trim();
                if (!value) {
                    inputValue.textContent = '-';
                    outputValue.textContent = 'Please enter text first';
                    return;
                }
                inputValue.textContent = value;
                const response = await fetch('/api/reverse/' + encodeURIComponent(value));
                const reversed = await response.text();
                outputValue.textContent = reversed;
            }

            button.addEventListener('click', runReverseTest);
            input.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') runReverseTest();
            });
        </script>
    """)

@app.route('/<random_string>')
def return_backwards_string(random_string):
    reversed_text = "".join(reversed(random_string))
    return page("Reverse Result", f"""
        <h1 class="headline box">Welcome to the Flask App</h1>
        <p class="subheadline box">Reverse string result page</p>

        <div class="result-box box">
            <p><strong>Input:</strong> {random_string}</p>
            <p><strong>Reversed:</strong> {reversed_text}</p>
        </div>

        <p class="helper box"><a href="/">Back to test</a></p>
    """)

@app.route('/api/reverse/<random_string>')
def reverse_string_api(random_string):
    return "".join(reversed(random_string))

@app.route('/get-mode')
def get_mode():
    mode_value = os.environ.get("MODE", "No mode set")
    return page("Mode Result", f"""
        <h1 class="headline box">Welcome to the Flask App</h1>
        <p class="subheadline box">Environment mode page</p>

        <div class="result-box box">
            <p><strong>MODE:</strong> {mode_value}</p>
        </div>

        <p class="helper box"><a href="/">Back to tester</a></p>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
