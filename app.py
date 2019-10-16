from flask import Flask, request, redirect
from requests.exceptions import HTTPError
import requests
import urllib
import json

app = Flask(__name__)

# base_oauth_url -- endpoint for initiating an OAuth flow
base_oauth_url = "https://app.pagerduty.com/oauth"

with open("config.json") as config_file:
    config = json.load(config_file)

# parameters to send to the `oauth/authorize` endpoint to initiate flow
auth_params = {
    "response_type": "code",
    "client_id": config["PD_CLIENT_ID"],
    "redirect_uri": config["REDIRECT_URI"],
}

auth_url = "{url}/authorize?{query_string}".format(
    url=base_oauth_url, query_string=urllib.parse.urlencode(auth_params)
)


@app.route("/")
def index():
    return '<h1>PagerDuty OAuth2 Sample</h1><a href="/auth">Connect to PagerDuty</a>'


@app.route("/auth")
def authenticate():
    return redirect(auth_url)


@app.route("/callback")
def callback():
    token_params = {
        "client_id": config["PD_CLIENT_ID"],
        "client_secret": config["PD_CLIENT_SECRET"],
        "redirect_uri": config["REDIRECT_URI"],
        "grant_type": "authorization_code",
        "code": request.args.get("code"),
    }

    html = "<h1>PagerDuty OAuth2 Sample</h1>"

    try:
        # Retrieve code and request access token
        token_res = requests.post(
            "{url}/token".format(url=base_oauth_url), params=token_params
        )

        token_res.raise_for_status()
        body = token_res.json()
        api_token = body["access_token"]

        headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": "Bearer " + api_token,
        }

        # Use the access token to make a call to the PagerDuty API
        user_res = requests.get("https://api.pagerduty.com/users/me", headers=headers)

        user_res.raise_for_status()
        body = user_res.json()

        html += "<div><img src='{avatar}' /> <h2>Hello, {name}!</h2></div>".format(
            avatar=body["user"]["avatar_url"], name=body["user"]["name"]
        )

    except HTTPError as e:
        print(e)
        html += "<p>{error}</p>".format(error=e)

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
