import hashlib

from sqlalchemy import Column, String, DateTime, UUID, ForeignKey
from sqlalchemy.orm import relationship

from shared.models import Base


class Item(Base):
    __tablename__ = 'RR_ITEM'
    hashcode = Column(String, nullable=False, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    link = Column(String, nullable=False)
    pub_date = Column(DateTime, nullable=False)
    feed_id = Column(UUID(as_uuid=True), ForeignKey('RR_FEED.id'), nullable=False)

    feed = relationship("Feed", back_populates="items")
    tokens = relationship("Token", back_populates="item", cascade="all, delete-orphan")

    def __init__(self, title, description, link, pub_date, feed_id, **kw):
        super().__init__(**kw)
        self.hashcode = hashlib.md5((title + description + link).encode('utf-8')).hexdigest()
        self.title = title
        self.description = description
        self.link = link
        self.pub_date = pub_date
        self.feed_id = feed_id


def exists(session, item: Item):
    return session.query(Item).filter(Item.hashcode == item.hashcode).first() is not None


def insert(session, item: Item):
    session.add(item)
    session.commit()
