import json
from tests.confest import client
from contacts.schemas import Contact, PostContact
from datetime import datetime, timedelta

def test_create_contact(client):
    data = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "johndoe@example.com",
        "phone": "+1234567890",
        "birthday": "1990-01-01"
    }
    response = client.post("/contacts", json=data)
    assert response.status_code == 200
    assert response.json()["email"] == "johndoe@example.com"

def test_get_all_contacts(client):
    response = client.get("/contacts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_contact_by_id(client):
    data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "email": "janedoe@example.com",
        "phone": "+0987654321",
        "birthday": "1995-05-15"
    }
    create_response = client.post("/contacts", json=data)
    contact_id = create_response.json()["id"]
    
    response = client.get(f"/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "janedoe@example.com"

def test_update_contact(client):
    data = {
        "firstname": "Alice",
        "lastname": "Smith",
        "email": "alicesmith@example.com",
        "phone": "+1122334455",
        "birthday": "1985-12-25"
    }
    create_response = client.post("/contacts", json=data)
    contact_id = create_response.json()["id"]

    new_data = {
        "firstname": "Alice",
        "lastname": "Johnson",
        "email": "alicejohnson@example.com",
        "phone": "+1122334455",
        "birthday": "1985-12-25"
    }
    response = client.put(f"/contacts/{contact_id}", json=new_data)
    assert response.status_code == 200
    assert response.json()[0]["email"] == "alicejohnson@example.com"

def test_delete_contact(client):
    data = {
        "firstname": "Bob",
        "lastname": "Brown",
        "email": "bobbrown@example.com",
        "phone": "+2233445566",
        "birthday": "1970-07-07"
    }
    create_response = client.post("/contacts", json=data)
    contact_id = create_response.json()["id"]

    response = client.delete(f"/contacts/{contact_id}")
    assert response.status_code == 200

def test_get_7_days_birthday_contact(client):
    # Create contacts with upcoming birthdays
    today = datetime.now()
    upcoming_birthdays = [
        {"firstname": "Tom", "lastname": "Thumb", "email": "tom@example.com", "phone": "+3344556677", "birthday": (today + timedelta(days=i)).strftime("%Y-%m-%d")}
        for i in range(7)
    ]
    for contact in upcoming_birthdays:
        client.post("/contacts", json=contact)
    
    response = client.get("/contacts/show_birthday")
    assert response.status_code == 200
    assert len(response.json()) == 7

def test_get_by_query(client):
    data = {
        "firstname": "Charlie",
        "lastname": "Day",
        "email": "charlieday@example.com",
        "phone": "+4455667788",
        "birthday": "1992-03-12"
    }
    client.post("/contacts", json=data)
    
    response = client.get("/contacts/query/Charlie")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_upload_image(client):
    # Create a contact to update avatar
    data = {
        "firstname": "Eve",
        "lastname": "White",
        "email": "evewhite@example.com",
        "phone": "+5566778899",
        "birthday": "2000-11-22"
    }
    create_response = client.post("/contacts", json=data)
    contact_id = create_response.json()["id"]

    with open("path/to/test_image.jpg", "rb") as img:
        response = client.post(f"/contacts/avatar?contact_id={contact_id}", files={"file": img})
    assert response.status_code == 200
    assert response.json()["ok"]

def test_clear_data(client):
    response = client.delete("/contacts/debug")
    assert response.status_code == 200

def test_fake_data_flud(client):
    response = client.post("/contacts/debug", params={"quantity": 5})
    assert response.status_code == 200
    assert len(response.json()) == 6
