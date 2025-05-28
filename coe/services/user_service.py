from sqlalchemy.orm import Session
from coe.models.user import User
from coe.schemas.user import CreateUser, UserLogin, UpdateUser
from coe.services.auth_service import create_access_token, create_refresh_token
import bcrypt

def create_user(user: CreateUser, db: Session) -> User:
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email, 
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def login_user(login_cred: UserLogin, db: Session) -> dict | None:
    print(login_cred.email)
    user = db.query(User).filter_by(email=login_cred.email).first()

    if not user:
        return None

    if not bcrypt.checkpw(login_cred.password.encode(), user.password.encode()):
        return None
    
    token_data = {"user_id": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def update_user(user_id: int, user_data: UpdateUser, db: Session) -> bool:
    user = db.query(User).filter_by(id=user_id).first()

    if not user:
        return False

    # Use dict and setattr to dynamically update only non-None fields
    update_fields = user_data.model_dump(exclude_unset=True, exclude={"id"})
    for field, value in update_fields.items():
        if field == 'password':
            value = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        setattr(user, field, value)

    db.commit()
    db.refresh(user) 

    return True

def remove_user(user_id: int, db: Session) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()

        return True
    
    return False
