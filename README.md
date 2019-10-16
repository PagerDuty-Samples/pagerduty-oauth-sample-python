# pagerduty-oauth-sample-python

This is a sample project to illustrate how to build a PagerDuty OAuth flow in Python 3 to authorize access to a user's PagerDuty account and data.

If you're an application builder, users of your application will need to access their PagerDuty data in a safe and secure way. This is done through an access token that can be [manually generated](https://support.pagerduty.com/docs/generating-api-keys) by the user in the PagerDuty UI. Or, you can provide an automated process by implementing an OAuth flow in your application.


## Enable OAuth
To enable OAuth for your application, you'll first need to register your app in the PagerDuty UI. Instructions for registering your application can be found in [How to Build an App](https://v2.developer.pagerduty.com/docs/how-to-build-an-app).

## Configure Sample
Once you have registered your App, there are a few key pieces of information you'll need to build your OAuth flow. In the **App Functionality** section you'll need to grab the value(s) for **Redirect URLs**, the **Client Id** and **Client Secret**. 

Take those three values and plug them into the `config.json` file in this project. 

```json
{
    "PD_CLIENT_ID": "<YOUR_CLIENT_ID_HERE>",
    "PD_CLIENT_SECRET": "<YOUR_CLIENT_SECRET_HERE>",
    "REDIRECT_URI": "http://localhost:5000/callback"
}
```
The value for `REDIRECT_URI` can use whichever domain you have this code running on, for our purposes of testing and exploring we'll use `http://localhost:5000` as the domain, and `/callback` is the endpoint our sample application uses to process the callback, so you'll need to keep that.


## Run Sample
To use this sample, you'll need to create a virtual environment,`python -m venv env`, and activate it `source env/bin/activate`. Then call `pip install -r requirements.txt` to install dependent modules.

Next, call `python app.py`, after which you should be greeted by a message that says, `Serving Flask app "app"`. 

In your browser, go to [http://localhost:5000](http://localhost:5000) where you'll see a link to `Connect to PagerDuty`. Click that to initiate the OAuth flow. You'll be taken to PagerDuty, where you'll be asked to login (if necessary), and then to authorize access of your PagerDuty account to the sample application.

If all goes well, the callback page on the sample should present a friendly welcome message, along with your avatar.

## The Code
Authorizing through OAuth involves making a request to PagerDuty for an authorization code. That request includes the Client ID that was generated when registering your app as well as the Redirect URI.

To initiate the flow make a `GET` call to `https://app.pagerduty.com/oauth/authorize` with the query string parameters listed in `auth_params` as seen below.

```python
base_oauth_url = "https://app.pagerduty.com/oauth"

with open("config.json") as config_file:
    config = json.load(config_file)

auth_params = {
    "response_type": "code",
    "client_id": config["PD_CLIENT_ID"],
    "redirect_uri": config["REDIRECT_URI"],
}

auth_url = "{url}/authorize?{query_string}".format(
    url=base_oauth_url, query_string=urllib.parse.urlencode(auth_params)
)
```
The values for `client_id` and `redirect_uri` are taken from `config.json`, and `response_type` is important as it tells PagerDuty what type of flow is being initiated. In this case, by setting `response_type: 'code'` the flow is an Authorization Grant Flow.

A successful response from calling the `https://app.pagerduty.com/oauth/authorize` endpoint should result in PagerDuty calling the `redirect_uri` you specified, which is the `/callback` in this project. The function at `/callback` is expecting PagerDuty to send a `code` in the query string. Using this `code` and the `PD_CLIENT_SECRET` in `config.json` you are now ready to request an access token. 

To request an access token from PagerDuty you'll `POST` the values from `token_params` shown below in the body of the request to `https://app.pagerduty.com/oauth/token`. 

```python
token_params = {
    "client_id": config["PD_CLIENT_ID"],
    "client_secret": config["PD_CLIENT_SECRET"],
    "redirect_uri": config["REDIRECT_URI"],
    "grant_type": "authorization_code",
    "code": request.args.get("code"),
}
```

Using the [requests](https://pypi.org/project/requests/) library this call looks like this:

```python
try:
    token_res = requests.post(
        "{url}/token".format(url=base_oauth_url), params=token_params
    )
    token_res.raise_for_status()
```
We use `try` and `except` blocks to check for any non-200 status codes and log them to the console:
```python
except HTTPError as e:
    print(e)
```
Then, using the requests library again the sample calls the [PagerDuty REST API](https://v2.developer.pagerduty.com/docs/rest-api) to get the current user, or the owner the of the access token.

```python
user_res = requests.get("https://api.pagerduty.com/users/me", headers=headers)

```

Hopefully, this sample helped to illustrate how to impliment an OAuth flow with PagerDuty using Python 3. Please post to the [Developer Forums](https://community.pagerduty.com/c/dev) if you get stuck or have any questions.