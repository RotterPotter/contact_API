from fastapi import APIRouter, Depends, Request, File, UploadFile
import contacts.schemas
import database
import contacts.models
from faker import Faker
from datetime import datetime
from limiter_config import limiter

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
import os 


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
@limiter.limit('5/minute')
async def get_all_contacts(
    request: Request,
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

@router.post("/avatar")
async def upload_image(
    contact_id: int,
    file: UploadFile = File(),
    db = Depends(database.get_db)
):
    load_dotenv()

    cloudinary.config( 
        cloud_name = os.environ.get('CLOUD_NAME'), 
        api_key = os.environ.get('CLOUD_KEY'), 
        api_secret = os.environ.get('CLOUD_SECRET'), 
        secure=True
    )

    req = cloudinary.uploader.upload(file.file, public_id="root", overwrite=True)

    src_url = cloudinary.CloudinaryImage('root').build_url(
        width=500, height=500, crop="auto", version=req.get('version')
    ) 

    user = db.query(contacts.models.Contact).filter_by(id=contact_id).first()
    user.avatar = src_url
    db.commit()
    return {'ok': True}


@router_debug.delete("") #drop contact-model metadata(tables, rows - data)
async def clear_data(
    db = Depends(database.get_db)
):
    engine = database.engine
    contacts.models.Contact.metadata.drop_all(engine)
    contacts.models.Contact.metadata.create_all(engine)
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
                                        "birthday": fake.date(),
                                        "avatar": None
                                        })
        
        db.add(new_contact)
        new_contacts.append(new_contact.__dict__)

    db.commit()
    return new_contacts
    


    
    