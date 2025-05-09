from typing import List, Optional

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy import DateTime, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship)


class Base(DeclarativeBase):
    pass

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=naming_convention)


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
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=True)
    is_moderator: Mapped[bool] = mapped_column(default=False, nullable=True)

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
    contact: Mapped[str] = mapped_column(String(), nullable=True)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tg_users.id'))
    user: Mapped[Optional["User"]] = relationship(back_populates='messages')
    additional_messages: Mapped[List['AdditionalMessages']] = relationship(
        back_populates='title_message', cascade='all, delete-orphan')
    serial_info_id: Mapped[Optional[int]] = mapped_column(ForeignKey('serial_nums.id'))
    serial_info: Mapped[Optional["AdvertSerialNums"]] = relationship(back_populates='title_messages')
    
    def update_from_tg_format(self, message: dict):
        tg_db_translater = {
            'content_type': 'mess_type',
            'space': 'space',
            'flour': 'flour',
            'material': 'material',
            'address': 'address',
            'year': 'year',
            'district': 'district',
            'price': 'price',
        }
        for key, value in message.items():
            db_key = tg_db_translater.get(key)
            if not db_key:
                continue
            vtype = value['content_type']
            setattr(self, db_key, value[vtype])

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
    blank_line_name: Mapped[str] = mapped_column(String(), nullable=True)
    sequence_num: Mapped[int] = mapped_column(default=0)
    enclosure_num: Mapped[int] = mapped_column(default=0)
    content_text: Mapped[str] = mapped_column(String(), nullable=True)

    def update_from_tg_format(self, message: dict):
        tg_db_translater = {
            'content_type': 'mess_type',
            'caption': 'caption',
            'text': 'content_text',
            'audio': 'content_text',
            'photo': 'content_text',
            'voice': 'content_text',
            'video': 'content_text',
            'document': 'content_text',
            'location': 'content_text',
            'contact': 'content_text',
            'sticker': 'content_text',
        }
        for key, value in message.items():
            db_key = tg_db_translater.get(key)
            if not db_key:
                continue
            setattr(self, db_key, value)


class Adverts(Base):
    __tablename__ = 'adverts'
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str]
    title_message_id: Mapped[int] = mapped_column(
        ForeignKey('title_messages.id')
        )

class AdvertSerialNums(Base):
    __tablename__ = 'serial_nums'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_mess_id: Mapped[str] = mapped_column(
                                String(), nullable=True, default='0')
    title_messages: Mapped[List["TitleMessages"]] = relationship(
        back_populates='serial_info'
        )

