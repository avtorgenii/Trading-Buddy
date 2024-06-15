from sqlalchemy import create_engine, ForeignKey, Table, Column, String, Integer, CHAR
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class Person(Base):
    __tablename__ = 'people'

    ssn = Column('ssn', Integer, primary_key=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    gender = Column('gender', CHAR)
    age = Column('age', Integer)

    def __init__(self, ssn, first_name, last_name, gender, age):
        self.ssn = ssn
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.age = age

    def __repr__(self):
        return f"({self.ssn}) {self.first_name} {self.last_name} ({self.gender}, {self.age})"


class Thing(Base):
    __tablename__ = 'things'
    tid = Column('tid', Integer, primary_key=True)
    description = Column('description', String)
    owner = Column(Integer, ForeignKey('people.ssn'))

    def __init__(self, tid, description, owner):
        self.tid = tid
        self.description = description
        self.owner = owner

    def __repr__(self):
        return f"({self.tid}) {self.description} owned by {self.owner}"


engine = create_engine("sqlite:///mydb.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

p1 = Person(124, "Mike", "Smith", "m", 35)
p2 = Person(463, "Jean", "Polnareff", "m", 25)
p3 = Person(561, "Joseph", "Joestar", "m", 55)

session.add(p1)
session.add(p2)
session.add(p3)

session.commit()

results = session.query(Person).filter(Person.last_name == "Smith" and Person.first_name == "Mike")

print(list(results))

t1 = Thing(1, "Car", p1.ssn)
session.add(t1)
session.commit()

results = session.query(Thing, Person).filter(Thing.owner == Person.ssn)

print(list(results))



