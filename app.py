#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from concurrent.futures.process import _threads_wakeups
from dataclasses import dataclass
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import select, func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
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

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

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

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  this_city = -1
  venues = db.session.query(Venue.city, Venue.state, Venue.id, Venue.name).order_by(Venue.city).all()
  print('all venues:', venues)
  for venue in venues:
    num_up_shows = db.session.query(Shows).filter(Shows.venue_id==venue.id, Shows.start_time > datetime.today()).count()
    venueData = {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': num_up_shows}
    if this_city >= 0 and venue.city == data[this_city]['city']:
      print(data[this_city])
      data[this_city]['venues'].append(venueData)
    else:
      this_city += 1
      data.append({'city': venue.city, 'state': venue.state, 'venues': list()})
      data[this_city]['venues'].append(venueData)
  print('returning data:', data)
  return render_template('pages/venues.html', areas=data);

  ## mock data 
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {}
  keyword = request.form.get('search_term')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%'+keyword+'%')).all()
  response['count'] = len(venues)
  response['data'] = []
  for venue in venues:
    venueData = {}
    venueData['id'] = venue.id
    venueData['name'] = venue.name
    num_up_shows = db.session.query(Shows).filter(Shows.venue_id==venue.id, Shows.start_time > datetime.today()).count()
    venueData['num_upcoming_shows'] = num_up_shows
    print(venueData)
    response['data'].append(venueData)
  return render_template('pages/search_venues.html', results=response, search_term=keyword)

  # # mock data
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  print('this venue:', venue)
  data = {
    'id': venue.id,
    'name': venue.name,
    'city': venue.city,
    'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'genres': venue.genres,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'website': venue.website,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description
  }
  data['past_shows'] = list()
  data['upcoming_shows'] = list()
  
  past_shows = db.session.query(Shows.artist_id, Shows.start_time).filter(Shows.venue_id == venue.id, Shows.start_time < datetime.today()).all()
  upcoming_shows = db.session.query(Shows.artist_id, Shows.start_time).filter(Shows.venue_id == venue.id, Shows.start_time >= datetime.today()).all()
  
  for show in past_shows:
    event = {}
    event['artist_id'] = show.artist_id
    event['artist_name'] = db.session.query(Artist).get(show.artist_id).name
    event['artist_image_link'] = db.session.query(Artist).get(show.artist_id).image_link
    event['start_time'] = str(show.start_time)
    data['past_shows'].append(event)
  
  for show in upcoming_shows:
    event = {}
    event['artist_id'] = show.artist_id
    event['artist_name'] = db.session.query(Artist).get(show.artist_id).name
    event['artist_image_link'] = db.session.query(Artist).get(show.artist_id).image_link
    event['start_time'] = str(show.start_time)
    data['upcoming_shows'].append(event)
  
  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  
  return render_template('pages/show_venue.html', venue=data)
  ## mock data
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
 form = VenueForm()
 return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm()
  error = False
  #the genre field from form submission is a list, convert list to string
  # # TODO: modify data to be the data object returned from db insertion
  try:
    newVenue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(newVenue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  else:
    # # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = db.session.query(Artist).all()
  print('all artists:', artists)
  for artist in artists:
    artistData = {'id': artist.id, 'name': artist.name}
    data.append(artistData)
  return render_template('pages/artists.html', artists=data)
  ## mock data    
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  keyword = request.form.get('search_term')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%'+keyword+'%')).all()
  response['count'] = len(artists)
  response['data'] = []
  for artist in artists:
    artistData = {}
    artistData['id'] = artist.id
    artistData['name'] = artist.name
    num_up_shows = db.session.query(Shows).filter(Shows.artist_id==artist.id, Shows.start_time > datetime.today()).count()
    artistData['num_upcoming_shows'] = num_up_shows
    print('matching artist', artistData)
    response['data'].append(artistData)
  return render_template('pages/search_artists.html', results=response, search_term=keyword)
  ## mock data
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  print('this artist:', artist)
  data = {
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'genres': artist.genres,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'website': artist.website,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description
    }
  data['past_shows'] = list()
  data['upcoming_shows'] = list()
  
  # past_shows and upcoming_shows are row objects as list of tuples
  past_shows = db.session.query(Shows.venue_id, Shows.start_time).filter(Shows.artist_id==artist.id, Shows.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Shows).filter(Shows.artist_id==artist.id, Shows.start_time >= datetime.now()).all()
  # print('past_shows:', past_shows)
  # print('upcoming_shows:', upcoming_shows)
  
  for show in past_shows:
    event = {}
    event['venue_id'] = show.venue_id
    event['venue_name'] = db.session.query(Venue).get(show.venue_id).name
    event['venue_image_link'] = db.session.query(Venue).get(show.venue_id).image_link
    event['start_time'] = str(show.start_time)
    data['past_shows'].append(event)
    #print('past event:', event)
  
  for show in upcoming_shows:
    event = {}
    event['venue_id'] = show.venue_id
    event['venue_name'] = db.session.query(Venue).get(show.venue_id).name
    event['venue_image_link'] = db.session.query(Venue).get(show.venue_id).image_link
    event['start_time'] = str(show.start_time)
    data['upcoming_shows'].append(event)
    #print('future event:', event)
    
  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  print('all artsit data:', data)
  return render_template('pages/show_artist.html', artist=data)

  ## mock data
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  error = False
  try:
    newArtist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(newArtist)
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  else:  
  # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully listed!')
  return render_template('pages/home.html')

#  Update Artist and Venue
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = db.session.query(Shows).order_by(Shows.start_time).all()
  print(shows)
  
  for show in shows:
    venue_name = db.session.query(Venue).get(show.venue_id).name
    artist_name = db.session.query(Artist).get(show.artist_id).name
    artist_image = db.session.query(Artist).get(show.artist_id).image_link
    showData = {
      'venue_id': show.venue_id,
      'venue_name': venue_name,
      'artist_id': show.artist_id,
      'artist_name': artist_name,
      'artist_image_link': artist_image,
      'start_time': str(show.start_time)
    }
    data.append(showData)
  return render_template('pages/shows.html', shows=data)
  
  ## mock data
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }]

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  error = False
  try:
    venue_id = form.venue_id.data
    artist_id = form.artist_id.data
    print(venue_id, artist_id)
    host = db.session.query(Venue).get(venue_id)
    performer = db.session.query(Artist).get(artist_id)
    print(host.name, performer.name)
    if host is not None and performer is not None:  
      newShow = Shows(start_time = form.start_time.data)
      newShow.venue = host
      newShow.artist = performer
      db.session.add(newShow)
      db.session.commit()
    else:
      flash('An error occurred. Can not find artist ID or venue ID.')
      return render_template('pages/home.html')
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  else:
    # # on successful db insert, flash success
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
