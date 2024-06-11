import json
from tests.confest import client


def test_create_contact(client):
    data = {"username":"testuser","email":"testuser@nofoobar.com","password":"testing"}
    response = client.post("/users/",json.dumps(data))
    assert response.status_code == 200 
    assert response.json()["email"] == "testuser@nofoobar.com"
    assert response.json()["is_active"] == True