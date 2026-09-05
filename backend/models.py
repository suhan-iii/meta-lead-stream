from datetime import datetime
from sqlalchemy import Column, String, DateTime
from database import Base


class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)