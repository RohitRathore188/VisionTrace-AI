import urllib.request
import json

req = urllib.request.Request(
    'http://localhost:8000/api/v1/search/text',
    data=json.dumps({
        'query_text': 'red bus',
        'top_k': 5,
        'video_ids': ['53d21b7b-2190-4887-a348-a45b0eb1cd3d'],
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
        print(f"Query: '{data['query_text']}'")
        print(f"Total Matches: {data['total_matches']}")
        for r in data['results']:
            print(f" - [{r['type']}] Video: {r['video_title']} ({r['video_id']}) | Cam: {r['camera_name']} | Score: {r['similarity_score']*100:.1f}% | Time: {r['timestamp_seconds']}s")
except Exception as e:
    print("Error:", e)
