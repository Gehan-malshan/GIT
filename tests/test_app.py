import copy
from fastapi.testclient import TestClient
import src.app as app_module
import pytest


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before each test to avoid cross-test pollution."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = copy.deepcopy(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Ensure a known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = "newstudent@mergington.edu"
    # Sign up for Chess Club
    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]

    # Attempting to sign the same student up for a different activity should fail
    resp2 = client.post(f"/activities/Programming Class/signup", params={"email": email})
    assert resp2.status_code == 400

    # Now unregister from Chess Club
    resp3 = client.delete(f"/activities/Chess Club/participants", params={"email": email})
    assert resp3.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_not_found():
    resp = client.delete(f"/activities/Chess Club/participants", params={"email": "noone@mergington.edu"})
    assert resp.status_code == 404


def test_signup_activity_not_found():
    resp = client.post(f"/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404
