from flask import Flask, request
import pdpyras

app = Flask(__name__)


@app.route("/")
def index():
    return '<h1>PagerDuty OAuth2 Sample</h1><a href="/auth">Connect to PagerDuty</a>'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
