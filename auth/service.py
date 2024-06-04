from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import database
import auth.models
import auth.schemas
import smtplib
from email.mime.text import MIMEText
from jinja2 import Template
from dotenv import load_dotenv
import os


class Service:

    crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY_EMAIL = os.environ.get('SECRET_KEY_EMAIL')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
    
# email vars
    subject = "Email Subject"
    template_path = "\\".join(__file__.split('\\')[:-1]) + r'\templates\verifie_email.html'


    def __init__(self):
        load_dotenv()
        print(os.environ.get('SENDER'))

    async def hash_password(self, password:str):
        return self.crypt_context.hash(password)
    
    async def create_access_token(self, data:dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_jwt
    
    def create_email_token(self, data:dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY_EMAIL, self.ALGORITHM)
        return encoded_jwt

    async def verify_password(self, plain_pwd: str, hashed_pwd:str):
        return self.crypt_context.verify(plain_pwd, hashed_pwd)
    
    def send_verification_email(self, email: str, db):
        email_token = self.create_email_token({'sub': email})
        email_token_model = auth.models.EmailToken(username=email, email_token=email_token)
        db.add(email_token_model)
        db.commit()

        sender_email = os.environ.get('SENDER')
        sender_password = os.environ.get('PASSWORD')
        recipient_email = email
        with open(self.template_path, 'r') as f:
            template = Template(f.read())
        context = {
            'subject': 'Hello from Python',
            'body': 'This is an email sent from Python using an HTML template and the Gmail SMTP server.'
        }
        html = template.render(context, email_token=email_token)
        html_message = MIMEText(html, 'html')
        html_message['Subject'] = context['subject']
        html_message['From'] = sender_email
        html_message['To'] = recipient_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, html_message.as_string())

    def verifie_email_token(self, token:str, db):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY_EMAIL, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            
            email_token_user = db.query(auth.models.EmailToken).filter_by(username=username).first()
            if email_token_user is None:
                raise credentials_exception
            
            if email_token_user.email_token == token:
                user = db.query(auth.models.User).filter_by(username=email_token_user.username).first()
                user.verified = True
                db.commit()
                return True
            return False

        except jwt.exceptions.InvalidTokenError:
            raise credentials_exception
        
        


        
    @classmethod
    async def get_current_user(
            self,
            token: str = Depends(oauth2_scheme),
            db= Depends(database.get_db)
        ):
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = auth.schemas.TokenData(username=username)
        except jwt.exceptions.InvalidTokenError:
            raise credentials_exception
        
        user = db.query(auth.models.User).filter_by(username=token_data.username).first()
        if user is None:
            raise credentials_exception
        if not user.verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Verifie your email address'
            )
        return user