from datetime import  datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Path, Query
from sqlalchemy import text, extract, or_, and_
from sqlalchemy.orm import Session
from models import Contact
from schemas import ContactSchema, ContactResponse
from db import get_db

app = FastAPI()


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/")
def main_root():
    return {"message": "Application Ver 0.0.1"}


@app.get("/contacts", response_model=list[ContactResponse], tags=["contacts"])
def get_contacts(
    first_name: Optional[str] = Query(None, title="First Name"),
    last_name: Optional[str] = Query(None, title="Last Name"),
    email: Optional[str] = Query(None, title="Email"),
    db: Session = Depends(get_db),
):
    query = db.query(Contact)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    contacts = query.all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactResponse, tags=["contacts"])
async def get_contact_by_id(
    contact_id: int = Path(ge=1), db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@app.post("/contacts", response_model=ContactResponse, tags=["contacts"])
async def create_contact(body: ContactSchema, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(email=body.email).first()
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Contact is existing!"
        )

    contact = Contact(**body.model_dump())
    db.add(contact)
    db.commit()
    return contact


@app.put("/contacts/{contact_id}", response_model=ContactResponse, tags=["contacts"])
async def update_contact(
    body: ContactSchema, contact_id: int = Path(ge=1), db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")

    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.phone_number = body.phone_number
    contact.birthday = body.birthday
    contact.additional_info = body.additional_info

    db.commit()
    return contact


@app.delete("/contacts/{contact_id}", response_model=ContactResponse, tags=["contacts"])
async def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")

    db.delete(contact)
    db.commit()
    return contact


@app.get(
    "/contacts/upcoming-birthdays/",
    response_model=List[ContactResponse],
    tags=["contacts"],
)
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = datetime.now().date()
    end_date = today + timedelta(days=7)

    if today.month == 12 and end_date.month == 1:
        contacts = (
            db.query(Contact)
            .filter(
                or_(
                    extract("month", Contact.birthday) == today.month,
                    extract("day", Contact.birthday) >= today.day,
                    extract("month", Contact.birthday) == end_date.month,
                    extract("day", Contact.birthday) <= end_date.day,
                )
            )
            .all()
        )
    else:
        contacts = (
            db.query(Contact)
            .filter(
                or_(
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) == end_date.month,
                        extract("day", Contact.birthday) <= end_date.day,
                    ),
                )
            )
            .all()
        )

    return contacts
