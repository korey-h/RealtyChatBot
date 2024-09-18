from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy import DateTime, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship)


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'tg_users'
    __mapper_args__ = {
        "batch": False
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(primary_key=False, unique=True)
    name: Mapped[str] = mapped_column(String(50))
    messages: Mapped[List['TitleMessages']] = relationship(
        back_populates='user', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'User: id={self.id}, name= {self.name}'

class TitleMessages(Base):
    __tablename__ = 'title_messages'
    __mapper_args__ = {
        "batch": False
    }
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_mess_id: Mapped[str] = mapped_column(String(),
                                            nullable=False, unique=True)
    time: Mapped[DateTime]= mapped_column(DateTime, nullable=False,)
    mess_type: Mapped[str]
    space: Mapped[int]
    flour: Mapped[int]
    material: Mapped[str]
    address: Mapped[str]
    year: Mapped[int]
    district: Mapped[str]
    price: Mapped[int]

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tg_users.id'))
    user: Mapped[Optional["User"]] = relationship(back_populates='messages')
    additional_messages: Mapped[List['AdditionalMessages']] = relationship(
        back_populates='title_message', cascade='all, delete-orphan')


class AdditionalMessages(Base):
    __tablename__ = 'additional_messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_mess_id: Mapped[str] = mapped_column(String(),
                                            nullable=False, unique=True)
    time: Mapped[DateTime]= mapped_column(DateTime, nullable=False,)
    mess_type: Mapped[str]
    caption: Mapped[str] = mapped_column(String(), nullable=True)
    title_message_id: Mapped[int] = mapped_column(
        ForeignKey('title_messages.id')
        )
    title_message: Mapped["TitleMessages"] = relationship(
        back_populates='additional_messages'
        )
    sequence_num: Mapped[int]
    enclosure_num: Mapped[int]