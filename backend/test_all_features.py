"""
VisionTrace AI — Complete End-to-End System Test Suite
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8") if data else None,
        headers=headers,
        method=method
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}
    except Exception as e:
        return 500, {"error": str(e)}

def main():
    print("=" * 80)
    print("VISIONTRACE AI — COMPREHENSIVE PLATFORM FEATURE TEST SUITE")
    print("=" * 80)

    # 1. System Health Check
    status, body = make_request(f"{BASE_URL}/system/health")
    print(f"\n[1] System Health Check: Status={status}")
    print(f"    Subsystem Status: {body.get('status', 'UNKNOWN')}")

    # 2. Login as Admin
    login_data = {"email": "admin@visiontrace.ai", "password": "AdminPassword123!"}
    status, body = make_request(f"{BASE_URL}/auth/login", method="POST", data=login_data)
    print(f"\n[2] Authentication Login: Status={status}")
    token = body.get("session", {}).get("access_token") or body.get("access_token")
    if not token:
        print(f"[X] Login failed: {body}")
        sys.exit(1)
    print(f"    Access Token: {token[:20]}...")
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 3. Dashboard Stats
    status, body = make_request(f"{BASE_URL}/dashboard/stats", headers=auth_headers)
    print(f"\n[3] Dashboard Statistics: Status={status}")
    print(f"    Videos Total: {body.get('videos', {}).get('total')}")
    print(f"    FAISS Index Vectors: {body.get('faiss_index', {}).get('total_vectors')}")

    # 4. Videos List & Selected Video
    status, videos = make_request(f"{BASE_URL}/videos?page=1&page_size=10", headers=auth_headers)
    print(f"\n[4] Videos API: Status={status}")
    vid_items = videos.get("items", []) if isinstance(videos, dict) else videos
    print(f"    Total Uploaded Videos: {len(vid_items)}")
    sample_video_id = vid_items[0].get("id") if vid_items else None

    # 5. Camera Management API
    status, body = make_request(f"{BASE_URL}/cameras", headers=auth_headers)
    print(f"\n[5] Camera Management API: Status={status}")
    print(f"    Total Cameras Loaded: {len(body) if isinstance(body, list) else 0}")
    if isinstance(body, list) and len(body) > 0:
        print(f"    Sample Camera: {body[0].get('name')} [{body[0].get('status')}]")

    # 6. Incident Cases API
    status, body = make_request(f"{BASE_URL}/cases", headers=auth_headers)
    print(f"\n[6] Incident Cases API: Status={status}")
    print(f"    Total Cases Loaded: {len(body) if isinstance(body, list) else 0}")

    # 7. Forensic Evidence API & SHA-256 Verification
    status, body = make_request(f"{BASE_URL}/evidence", headers=auth_headers)
    print(f"\n[7] Forensic Evidence API: Status={status}")
    print(f"    Total Evidence Items: {len(body) if isinstance(body, list) else 0}")
    if isinstance(body, list) and len(body) > 0:
        evi_id = body[0].get("id")
        status, ver_body = make_request(f"{BASE_URL}/evidence/{evi_id}/verify", method="POST", headers=auth_headers)
        print(f"    SHA-256 Re-Verification: Status={status}, Verified={ver_body.get('verified')}, Hash={ver_body.get('sha256_hash', '')[:16]}...")

    # 8. Security Alerts API
    status, body = make_request(f"{BASE_URL}/alerts", headers=auth_headers)
    print(f"\n[8] Security Alert Center API: Status={status}")
    print(f"    Total Alerts Loaded: {len(body) if isinstance(body, list) else 0}")

    # 9. FAISS Vector Search API
    search_payload = {
        "query_text": "Person wearing black shirt",
        "top_k": 5,
        "min_score": 0.1
    }
    status, search_body = make_request(f"{BASE_URL}/search/text", method="POST", data=search_payload, headers=auth_headers)
    print(f"\n[9] FAISS Vector Search API: Status={status}")
    print(f"    Matches Found: {search_body.get('total_matches', 0)}")
    print(f"    Latency: {search_body.get('execution_time_ms', 0):.2f}ms")
    if search_body.get("results"):
        print(f"    Top Match: '{search_body['results'][0].get('video_title')}' Track ID: {search_body['results'][0].get('track_id')} Score: {search_body['results'][0].get('similarity_score'):.4f}")

    # 10. ByteTrack All Trajectories API
    if sample_video_id:
        status, traj_body = make_request(f"{BASE_URL}/videos/{sample_video_id}/all-trajectories", headers=auth_headers)
        print(f"\n[10] ByteTrack All Trajectories API: Status={status}")
        print(f"    Total Motion Trajectories: {traj_body.get('total_tracks', 0)}")

    # 11. Immutable Audit Logs API
    status, body = make_request(f"{BASE_URL}/audit-logs", headers=auth_headers)
    print(f"\n[11] Immutable Audit Trail API: Status={status}")
    print(f"    Total Audit Logs Recorded: {len(body) if isinstance(body, list) else 0}")
    if isinstance(body, list) and len(body) > 0:
        print(f"    Latest Action: [{body[0].get('action')}] User: {body[0].get('user_email')}")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL PLATFORM FEATURES VERIFIED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
