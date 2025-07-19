import requests

response = requests.post(
    "http://127.0.0.1:8000/fetch_insights/",
    json={"website_url": "https://www.gymshark.com/"}
)

print(response.status_code)
print(response.json())
