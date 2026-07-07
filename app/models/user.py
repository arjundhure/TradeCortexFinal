from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    investor_type = Column(String(20), default="moderate")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def full_name(self) -> str:
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return name or self.email.split("@")[0]    
