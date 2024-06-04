from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import database
import auth.schemas
import auth.models
import auth.service
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer


auth_service = auth.service.Service()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # dependencies=[Depends(auth_service.get_current_user)]
)

router_debug = APIRouter(
    prefix="/auth_debug",
    tags=["auth debug"],
    # dependencies=[Depends(auth_service.get_current_user)]
)



"""
1. Create route for creating user
2. Verify email and password
3. Create access token 
4. return token

"""
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: auth.schemas.User,
    background_tasks: BackgroundTasks,
    db=Depends(database.get_db)
):
    if db.query(auth.models.User).filter_by(username=user.username).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User already exists'
        )
    
    hashed_password = await auth_service.hash_password(user.password)
    user_model = auth.models.User(username=user.username, hashed_password=hashed_password, access_token=None)
    
    background_tasks.add_task(auth_service.send_verification_email, user.username, db)
    db.add(user_model)
    db.commit()

@router.post("/token")
async def login_user(
    user_form: OAuth2PasswordRequestForm = Depends(),
    db = Depends(database.get_db)
):
    user = db.query(auth.models.User).filter_by(username=user_form.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User is not registered'
        )
    
    if not await auth_service.verify_password(user_form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid password'
        )
    
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='verifie your email address'
        )
    
    access_token = await auth_service.create_access_token(data={'sub': user_form.username})

    return auth.schemas.Token(access_token=access_token, token_type='bearer')

@router.get("/email_verification/{email_token}")
async def verifie_email(
    email_token: str,
    db = Depends(database.get_db)
):
    if auth_service.verifie_email_token(email_token, db):
        return {'detail': 'Access'}



"""
Debug part
"""
@router_debug.get('')
async def get_users(
    db = Depends(database.get_db)
): # get all users
    return [user for user in db.query(auth.models.User).all()]

