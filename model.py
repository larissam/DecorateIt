from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref, sessionmaker

Base = declarative_base()

ENGINE = create_engine("sqlite:///purikuras.db", echo=True)
Session = sessionmaker(bind=ENGINE)

session = Session()

class Purikura(Base):
  __tablename__ = "purikuras"
  id = Column(Integer, primary_key = True)
  user_id = Column(Integer, ForeignKey('users.id'))
  combined_src = Column(String(64), nullable=True)
  background_src = Column(String(64), nullable=True)
  foreground_src = Column(String(64), nullable=True)

  user = relationship("User",
          backref=backref("purikuras", order_by=id))

class User(Base):
  __tablename__ = "users"
  id = Column(Integer, primary_key = True)
  email = Column(String(64), nullable=False)
  password = Column(String(64), nullable=False)

# def connect():
#   global ENGINE
#   global Session

#   ENGINE = create_engine("sqlite:///purikuras.db", echo=True)
#   Session = sessionmaker(bind=ENGINE)

#   return Session()

def main():
  pass

if __name__ == "main":
  main()