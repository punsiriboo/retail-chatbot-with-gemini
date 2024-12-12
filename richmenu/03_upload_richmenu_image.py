import requests

richMenuId = "richmenu-96b2baf4159b57b22ae4b75200079430"
url = f"https://api-data.line.me/v2/bot/richmenu/{richMenuId}/content"

with open("richmenu/richmenu_json/2.jpg", "rb") as image:
  f = image.read()
payload = f
headers = {
  'Authorization': 'Bearer YAHHaUjhaSAPbSBbZSbZr7NL8JffU3pzRz8UousYTPthRzaSi7QLAxDe3F4NVyhFGF0vXapH3kuCA0Na5+OMQn1qeGUGYNCaOxBaYz6ZLPR9mFnQCSKxV2+z8FAj3ueN+/tQE/EGa9LZdsLJlbBMG49PbdgDzCFqoOLOYbqAITQ=',
  'Content-Type': 'image/jpeg'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
print(response)
