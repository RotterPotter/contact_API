from fastapi import APIRouter, Depends
import contacts.schemas
import database
import contacts.models
from faker import Faker
from datetime import datetime

fake = Faker()

router = APIRouter(prefix='/contacts', tags=['contacts'])
router_debug = APIRouter(prefix='/contacts/debug', tags=['contacts debug'])

@router.post("")
async def post_contact(
    contact: contacts.schemas.PostContact,
    db = Depends(database.get_db)
): #create contact
    new_contact = contacts.models.Contact(**contact.model_dump())
    db.add(new_contact)
    db.commit()
    return contact


@router.get("")
async def get_all_contacts(
    db = Depends(database.get_db)
): #get all contacts
    return [i for i in db.query(contacts.models.Contact).all()]

@router.get("{contact_id}")
async def get_contact_by_id(
    contact_id:int,
    db = Depends(database.get_db)
    ): #get contact by param
    return db.query(contacts.models.Contact).filter_by(id=contact_id).first()

@router.put("{contact_id}")
async def update_contact(
    contact_id: int,
    new_contact: contacts.schemas.Contact,
    db = Depends(database.get_db),
): #update existing contact
    contact = db.query(contacts.models.Contact).filter_by(id=contact_id)
    contact.update(new_contact.__dict__)
    db.commit()
    return contact.all()

@router.delete("{contact_id}")
async def delete_contact(
    contact_id: int,
    db = Depends(database.get_db)
): #delete contact by id
    contact = db.query(contacts.models.Contact).filter_by(id=contact_id)
    contact.delete()
    db.commit()


@router.get("/show_birthday")
async def get_7_days_birthday_contact(
    db = Depends(database.get_db)
): 
    date_now = datetime.now()
    all_contacts = db.query(contacts.models.Contact).all()

    matched_contacts = []
    for contact in all_contacts:
        birthday_lst = contact.birthday.split('-')
        birthday = datetime(date_now.year, int(birthday_lst[1]), int(birthday_lst[2]))

        if birthday < date_now:
            birthday = datetime(date_now.year + 1, int(birthday_lst[1]), int(birthday_lst[2]))               

        if 0 <= (birthday - date_now).days <= 7:
            matched_contacts.append(contact)
    
    return matched_contacts

@router.get("/query/{query}")
async def get_by_query(
    query: str,
    db = Depends(database.get_db)
):
    all_contacts = db.query(contacts.models.Contact).all()
    
    matched = list()
    for contact in all_contacts:
        for value in contact.__dict__.values(): # can be optimized
            if str(value) == query:
                matched.append(contact)

    return matched 



@router_debug.delete("") #drop contact-model metadata(tables, rows - data)
async def clear_data(
    db = Depends(database.get_db)
):
    contacts.models.Contact.metadata.drop_all()
    contacts.models.Contact.metadata.create_all()
    db.commit()

@router_debug.post("") # put some test data into database
async def fake_data_flud(
    db = Depends(database.get_db),
    quantity:int = 5
):
    new_contacts = list()
    for _ in range(quantity+1):
        new_contact = contacts.models.Contact(**{"firstname": fake.first_name(),
                                        "lastname": fake.last_name(),
                                        "email": fake.email(),
                                        "phone": fake.phone_number(),
                                        "birthday": fake.date()
                                        })
        
        db.add(new_contact)
        new_contacts.append(new_contact.__dict__)

    db.commit()
    return new_contacts
    


    
    