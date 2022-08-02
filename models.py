from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def setup_db(app, config_filename):
    app.config.from_object(config_filename)
    # The init_app method is used to support the factory pattern for creating apps
    db.init_app(app)

class Shows(db.Model):
  __tablename__ = 'Shows'
  venue_id = db.Column(db.ForeignKey('Venue.id', ondelete='CASCADE'), primary_key=True)
  artist_id = db.Column(db.ForeignKey('Artist.id', ondelete='CASCADE'), primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  venue = db.relationship('Venue', back_populates='shows')
  artist = db.relationship('Artist', back_populates='shows')

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String(120), dimensions=1), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default = False)
  seeking_description = db.Column(db.Text)
  shows = db.relationship('Shows', back_populates='venue', cascade='all, delete')

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String(120), dimensions=1), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default = False)
  seeking_description = db.Column(db.Text)
  shows = db.relationship('Shows', back_populates='artist', cascade='all, delete')