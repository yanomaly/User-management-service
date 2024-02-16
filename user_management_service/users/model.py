import enum
import uuid

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from user_management_service.database import Base


class Role(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class User(Base):
    __tablename__ = "users"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = sa.Column(sa.String, nullable=False)
    surname = sa.Column(sa.String, nullable=False, index=True)
    username = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    prone_number = sa.Column(sa.String)
    email = sa.Column(sa.String)
    role = sa.Column(sa.Enum(Role))
    group = relationship("Group", back_populates="users")
    group_id = sa.Column(sa.UUID, ForeignKey("roles.id"))
    image = sa.Column(sa.String)
    is_blocked = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime)
    modified_at = sa.Column(sa.DateTime)


class Group(Base):
    __tablename__ = "roles"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = sa.Column(sa.String, nullable=False)
    users = relationship("User", back_populates="group")
    created_at = sa.Column(sa.DateTime)
