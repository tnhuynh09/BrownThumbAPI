"""SQLAlchemy models for Brown Thumb."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    plants_owned = db.relationship('UserPlant', backref='user')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls, username, password, image_url):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            image_url=image_url,
        )

        try:
            db.session.add(user)
            db.session.commit()
            
            return user
        
        except IntegrityError as e:
            
            return None

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "imageUrl": self.image_url,
        }

class Plant(db.Model):
    """Plants saved from an external database."""

    __tablename__ = 'plants'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    plant_api_id = db.Column(
        db.Integer,
        nullable=False,
    )

    common_name = db.Column(
        db.Text,
    )

    scientific_name = db.Column(
        db.Text,
    )

    family = db.Column(
        db.Text,
    )

    family_common_name = db.Column(
        db.Text,
    )

    genus = db.Column(
        db.Text,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    plants_owned = db.relationship('UserPlant', backref='plants')

    def to_json(self):
        return {
            "id": self.id,
            "plantApiId": self.plant_api_id,
            "commonName": self.common_name,
            "scientificName": self.scientific_name,
            "family": self.family,
            "familyCommonName": self.family_common_name,
            "genus": self.genus,
            "imageUrl": self.image_url,
        }

class ProgressJournal(db.Model):
    """Journal for each plants that the user add to their profile."""

    __tablename__ = 'progress_journals'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.String(100),
        nullable=False,
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    notes = db.Column(
        db.String(300),
        nullable=False,
    )

    journal_entry = db.relationship('PlantJournal', backref='progress_journals')

class UserPlant(db.Model):
    """References the plants that each user added."""

    __tablename__ = 'users_plants'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    plant_id = db.Column(
        db.Integer,
        db.ForeignKey('plants.id', ondelete='CASCADE'),
        nullable=False,
    )

    date_purchased = db.Column(
        db.DateTime,
        default=datetime.utcnow(),
    )

    light_amt_req = db.Column(
        db.String(100),
    )

    water_amt_req = db.Column(
        db.String(100),
    )

    common_pests = db.Column(
        db.String(100),
    )

    notes = db.Column(
        db.String(100),
    )

    journal_entry = db.relationship('PlantJournal', backref='users_plants')

class PlantJournal(db.Model):
    """Reference the journals added to each plants."""

    __tablename__ = 'plants_journals'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_plant_id = db.Column(
        db.Integer,
        db.ForeignKey('users_plants.id', ondelete='CASCADE'),
        nullable=False,
    )

    journal_id = db.Column(
        db.Integer,
        db.ForeignKey('progress_journals.id', ondelete='CASCADE'),
        nullable=False,
    )

    def to_json(self):
        return {
            "id": self.id,
            "plantId": self.username,
            "JournalId": self.image_url,
        }

def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)