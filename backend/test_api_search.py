import urllib.request
import urllib.error
import json

req = urllib.request.Request(
    'http://localhost:8000/api/v1/search/text',
    data=json.dumps({
        'query_text': 'Person wearing black shirt',
        'top_k': 12,
        'min_score': 0.15
    }).encode('utf-8'),
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mock_token'
    }
)

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(data, indent=2))
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code)
    print("Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
