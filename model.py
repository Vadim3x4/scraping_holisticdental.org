from peewee import *

db = SqliteDatabase('people.db')

class Person(Model):
    person_email = CharField()
    firstname = CharField()
    lastname = CharField()
    person_link = CharField()
    person_location_street= CharField()
    person_location = CharField()
    person_phone = CharField()

    class Meta:
        database = db


Person.create_table()