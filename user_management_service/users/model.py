import datetime
import enum
import uuid
from dataclasses import dataclass

import sqlalchemy as sa
from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Role(enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


@dataclass
class Group(Base):
    __tablename__ = "roles"

    id: uuid = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = sa.Column(sa.String, nullable=False)
    users = relationship("User", back_populates="group")
    created_at: datetime = sa.Column(sa.DateTime)


@dataclass
class User(Base):
    __tablename__ = "users"

    id: uuid = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = sa.Column(sa.String, nullable=False)
    surname: str = sa.Column(sa.String, nullable=False, index=True)
    username: str = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    phone_number: str = sa.Column(sa.String, unique=True)
    email: str = sa.Column(sa.String, unique=True)
    role: Role = sa.Column(sa.Enum(Role))
    group = relationship("Group", back_populates="users")
    group_id: uuid = sa.Column(sa.UUID, ForeignKey("roles.id"))
    image: str = sa.Column(sa.String)
    is_blocked: bool = sa.Column(sa.Boolean, default=False)
    created_at: datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at: datetime = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
