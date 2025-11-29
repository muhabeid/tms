import urllib.request
import json
import urllib.error

BASE_URL = "http://localhost:8001/api/v1/workshop"

def make_request(method, url, data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.data = json_data

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
            else:
                print(f"Request failed with status: {response.status}")
                return None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None

def test_create_job():
    print("Testing Create Job...")
    payload = {
        "title": "Tire Replacement",
        "status": "pending",
        "description": "Replace all 4 tires",
        "cost": 500
    }
    response = make_request("POST", f"{BASE_URL}/jobs", payload)
    if response:
        print("Create Job: SUCCESS")
        print(response)
        return response["id"]
    return None

def test_list_jobs():
    print("\nTesting List Jobs...")
    response = make_request("GET", f"{BASE_URL}/jobs")
    if response is not None:
        print("List Jobs: SUCCESS")
        print(response)

def test_update_job(job_id):
    print(f"\nTesting Update Job {job_id}...")
    payload = {
        "status": "in_progress"
    }
    response = make_request("PUT", f"{BASE_URL}/jobs/{job_id}", payload)
    if response:
        print("Update Job: SUCCESS")
        print(response)

def test_delete_job(job_id):
    print(f"\nTesting Delete Job {job_id}...")
    response = make_request("DELETE", f"{BASE_URL}/jobs/{job_id}")
    if response:
        print("Delete Job: SUCCESS")
        print(response)

if __name__ == "__main__":
    job_id = test_create_job()
    if job_id:
        test_list_jobs()
        test_update_job(job_id)
        test_delete_job(job_id)
