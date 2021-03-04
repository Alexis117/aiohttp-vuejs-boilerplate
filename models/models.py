from gino.ext.aiohttp import Gino

db = Gino()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.String())