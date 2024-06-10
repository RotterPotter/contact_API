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
): 
    """
    Create a new contact.
    
    Args:
        contact (contacts.schemas.PostContact): The contact details to be created.
        db: Database session dependency.

    Returns:
        contacts.schemas.PostContact: The created contact.
    """
    new_contact = contacts.models.Contact(**contact.model_dump())
    db.add(new_contact)
    db.commit()
    return contact


@router.get("")
@limiter.limit('5/minute')
async def get_all_contacts(
    request: Request,
    db = Depends(database.get_db)
): 
    """
    Retrieve all contacts.

    Args:
        request (Request): The HTTP request object.
        db: Database session dependency.

    Returns:
        list: A list of all contacts.
    """
    return [i for i in db.query(contacts.models.Contact).all()]

@router.get("{contact_id}")
async def get_contact_by_id(
    contact_id:int,
    db = Depends(database.get_db)
): 
    """
    Retrieve a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db: Database session dependency.

    Returns:
        contacts.models.Contact: The contact with the specified ID.
    """
    return db.query(contacts.models.Contact).filter_by(id=contact_id).first()

@router.put("{contact_id}")
async def update_contact(
    contact_id: int,
    new_contact: contacts.schemas.Contact,
    db = Depends(database.get_db),
): 
    """
    Update an existing contact.

    Args:
        contact_id (int): The ID of the contact to update.
        new_contact (contacts.schemas.Contact): The new contact details.
        db: Database session dependency.

    Returns:
        list: The updated contact.
    """
    contact = db.query(contacts.models.Contact).filter_by(id=contact_id)
    contact.update(new_contact.__dict__)
    db.commit()
    return contact.all()

@router.delete("{contact_id}")
async def delete_contact(
    contact_id: int,
    db = Depends(database.get_db)
): 
    """
    Delete a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db: Database session dependency.

    Returns:
        None
    """
    contact = db.query(contacts.models.Contact).filter_by(id=contact_id)
    contact.delete()
    db.commit()


@router.get("/show_birthday")
async def get_7_days_birthday_contact(
    db = Depends(database.get_db)
): 
    """
    Retrieve contacts with birthdays in the next 7 days.

    Args:
        db: Database session dependency.

    Returns:
        list: A list of contacts with upcoming birthdays.
    """
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
    """
    Retrieve contacts matching a specific query.

    Args:
        query (str): The query string to search for.
        db: Database session dependency.

    Returns:
        list: A list of contacts matching the query.
    """
    all_contacts = db.query(contacts.models.Contact).all()
    
    matched = list()
    for contact in all_contacts:
        for value in contact.__dict__.values(): 
            if str(value) == query:
                matched.append(contact)

    return matched 

@router.post("/avatar")
async def upload_image(
    contact_id: int,
    file: UploadFile = File(),
    db = Depends(database.get_db)
):
    """
    Upload an avatar image for a contact.

    Args:
        contact_id (int): The ID of the contact to update.
        file (UploadFile): The image file to upload.
        db: Database session dependency.

    Returns:
        dict: A dictionary indicating success.
    """
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


@router_debug.delete("") 
async def clear_data(
    db = Depends(database.get_db)
):
    """
    Drop all contact data and recreate the contact table.

    Args:
        db: Database session dependency.

    Returns:
        None
    """
    engine = database.engine
    contacts.models.Contact.metadata.drop_all(engine)
    contacts.models.Contact.metadata.create_all(engine)
    db.commit()

@router_debug.post("") 
async def fake_data_flud(
    db = Depends(database.get_db),
    quantity:int = 5
):
    """
    Populate the database with fake contact data for testing.

    Args:
        db: Database session dependency.
        quantity (int, optional): Number of fake contacts to create. Defaults to 5.

    Returns:
        list: A list of the created fake contacts.
    """
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
