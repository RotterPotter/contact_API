import unittest
from contacts.routes import post_contact
from testdatabase import get_db
from contacts.schemas import PostContact
from tests.test_models import Contact

class PostContactTest(unittest.IsolatedAsyncioTestCase):
    DBsession = get_db()

    """
    1. Check that user successfully aded in database
    2. Check that if there new user with the same email that already exists
        raises conflict error.
    """
    async def test_contact_created(self):
        contact = PostContact(
            firstname='sasha',
            lastname='nazarevych',
            email='kivil@gmail.com',
            phone='+393488404117',
            birthday='2006-09-05'
        )
        post_contact(contact=contact, db=self.DBsession)
        contact_in_db = self.DBsession.query(Contact).first()
        self.assertTrue(contact_in_db)




