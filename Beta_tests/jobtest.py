import requests
import base64
import json

url = "https://jobs-api14.p.rapidapi.com/v2/list"

# Encode the page number as a Base64 string
page_number = 1
next_page = base64.b64encode(json.dumps({"page": page_number}).encode()).decode()

querystring = {
    "autoTranslateLocation": "true",
    "remoteOnly": "false",
    "employmentTypes": "fulltime;parttime;intern;contractor",
    "nextPage": next_page
}

headers = {
    "x-rapidapi-key": "b815418ce8msh7fc78b522c7e498p148f5ajsn1698d2f5b3f2",
    "x-rapidapi-host": "jobs-api14.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
data = response.json()

print(data)  # Print the results