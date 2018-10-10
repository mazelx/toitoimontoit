import datetime

from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('database.sqlite')


class Annonce(Model):
    # id = "pap-123456789"
    id = CharField(unique=True, primary_key=True)
    # site = [pap, lbc, logic-immo, seloger]
    site = CharField()
    created = DateTimeField()
    title = CharField()
    description = TextField(null=True)
    telephone = TextField(null=True)
    price = FloatField()
    surface = FloatField()
    rooms = IntegerField(null=True)
    bedrooms = IntegerField(null=True)
    city = CharField()
    link = CharField()
    picture = CharField(null=True)
    picturehash = CharField(null=True)
    posted2trello = BooleanField(default=False)
    isduplicate = BooleanField(default=False)
    idtrello = CharField(null=True)

    class Meta:
        database = db
        order_by = ('-created',)


def create_tables():
    with db:
        db.create_tables([Annonce])
