import os
from unittest import TestCase
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError
from models import db, User, Plant, ProgressJournal, UserPlant, PlantJournal

os.environ['DATABASE_URL'] = "postgresql:///brown_thumb"

from app import app

db.create_all()

class BrownThumbTestCase(TestCase):
    """Tests for Brown Thumb."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        # CREATE USER 
        user1 = User.signup("test_username", "test_password", "")
        user_id = 1111
        user1.id = user_id
        
        db.session.add(user1)
        db.session.commit()

        self.user1 = user1
        self.user_id = user_id

        # CREATE PLANT

        plant1 = Plant(
            plant_api_id=155724,
            common_name="water mint",
            scientific_name="Mentha aquatica",
            family="Lamiaceae",
            family_common_name="Mint family",
            genus="Mentha",
            image_url="https://bs.floristic.org/image/o/04fdf5bbfec0530275456e500ef895fd02514de6"
        )

        plant_id = 2222
        plant1.id = plant_id

        db.session.add(plant1)
        db.session.commit()

        self.plant1 = plant1
        self.plant_id = plant_id

        # CREATE USER PLANT

        user_plant1 = UserPlant(
            user_id=self.user_id,
            plant_id=self.plant_id,
        )

        user_plant_id = 3333
        user_plant1.id = user_plant_id

        db.session.add(user_plant1)
        db.session.commit()

        self.user_plant1 = user_plant1
        self.user_plant_id = user_plant_id

        # CREATE PROGRESS JOURNAL
        journal1 = ProgressJournal(
            title="test title journal",
            image_url="test.png",
            notes="test notes journal",
        )

        journal_id = 4444
        journal1.id = journal_id

        db.session.add(journal1)
        db.session.commit()

        self.journal1 = journal1
        self.journal_id = journal_id

        # CREATE PLANT JOURNAL 
        plant_journal1 = PlantJournal(
            user_plant_id=self.user_plant_id,
            journal_id=self.journal_id,
        )

        plant_journal_id = 5555
        plant_journal1.id = plant_journal_id

        db.session.add(plant_journal1)
        db.session.commit()

        self.plant_journal1 = plant_journal1
        self.plant_journal_id = plant_journal_id

        self.client = app.test_client()

    def tearDown(self):
        result = super().tearDown()
        db.session.rollback()
        return result

# **************************
# USER MODEL TEST 

    def test_user_model(self):
        """Test user model."""

        user = User(
            username="testusername10",
            password="testpassword",
            image_url="https://picsum.photos/seed/picsum/200/300"
        )

        db.session.add(user)
        db.session.commit()

        # User should have no plants
        self.assertEqual(len(user.plants_owned), 0)

        print("*******************************")
        print("test --- test_user_model")
        print("*******************************")

    def test_valid_signup(self):
        """Test user signup."""

        user_test = User.signup("test_username777", "test_password777", None)
        user_id2 = 7777
        user_test.id = user_id2
        db.session.commit()

        user_test = User.query.get(user_id2)

        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username, "test_username777")
        self.assertNotEqual(user_test.password, "test_password777")
        self.assertEqual(user_test.image_url, "http://brown-thumb-api.herokuapp.com/static/images/profile-default.png")
        # Bcrypt strings should start with $2b$
        self.assertTrue(user_test.password.startswith("$2b$"))

        print("*******************************")
        print("test --- test_valid_signup")
        print("*******************************")

    def test_invalid_username_signup(self):
        """Test empty username on signup."""

        invalid = User.signup(None, "test_password777", None)

        self.assertEqual(invalid, None)

        print("*******************************")
        print("test --- test_invalid_username_signup")
        print("*******************************")
    
    def test_invalid_password_signup(self):
        """Test empty password on signup."""

        with self.assertRaises(ValueError) as context:
            User.signup("testtest", None, None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "", None)

        print("*******************************")
        print("test --- test_invalid_password_signup")
        print("*******************************")
    
    def test_valid_authentication(self):
        """Test valid authentication."""
        
        user = User.authenticate(self.user1.username, "test_password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1.id)

        print("*******************************")
        print("test --- test_valid_authentication")
        print("*******************************")
    
    def test_invalid_username(self):
        """Test invalid username authentication."""

        self.assertFalse(User.authenticate("invalid_username", "password"))

        print("*******************************")
        print("test --- test_invalid_username")
        print("*******************************")

    def test_wrong_password(self):
        """Test invalid username authentication."""

        self.assertFalse(User.authenticate(self.user1.username, "invalid_password"))

        print("*******************************")
        print("test --- test_wrong_password")
        print("*******************************")

# **************************
# PLANT MODEL TEST 

    def test_plant_model(self):
        """Test plant model."""

        plant = Plant(
            plant_api_id=175704,
            common_name="field rose",
            scientific_name="Rosa arvensis",
            family="Rosaceae",
            family_common_name="Rose family",
            genus="Rosa",
            image_url="https://bs.floristic.org/image/o/afc9f4d7ce137f04746413f629330948b73e79d3"
        )

        db.session.add(plant)
        db.session.commit()

        self.assertIsNotNone(plant)

        print("*******************************")
        print("test --- test_plant_model")
        print("*******************************")

# **************************
# USER_PLANT MODEL TEST 

    def test_user_plant_model(self):
        """Test user_plant model."""
        
        user_plant = UserPlant(
            user_id=self.user_id,
            plant_id=self.plant_id,
        )

        db.session.add(user_plant)
        db.session.commit()

        # User should have 2 plant owned 
        # One here and another one in the setup 
        self.assertEqual(len(self.user1.plants_owned), 2)
        self.assertIsNotNone(user_plant)

        print("*******************************")
        print("test --- test_user_plant_model")
        print("*******************************")

# **************************
# PROGRESS JOURNAL MODEL TEST 

    def test_progress_journal_model(self):
        """Test progress journal model."""

        journal2 = ProgressJournal(
            title="test title journal",
            image_url="test.png",
            notes="test notes journal",
        )

        db.session.add(journal2)
        db.session.commit()

        self.assertIsNotNone(journal2)

        print("*******************************")
        print("test --- test_progress_journal_model")
        print("*******************************")

# **************************
# PLANT_JOURNAL MODEL TEST 

    def test_plant_journal_model(self):
        """Test user_plant model."""

        journal3 = ProgressJournal(
            title="test title journal",
            image_url="test.png",
            notes="test notes journal",
        )

        db.session.add(journal3)
        db.session.commit()
        
        plant_journal2 = PlantJournal(
            user_plant_id=self.user_plant_id,
            journal_id=journal3.id,
        )

        db.session.add(plant_journal2)
        db.session.commit()

        self.assertEqual(len(self.user_plant1.journal_entry), 2)
        self.assertIsNotNone(plant_journal2)

        print("*******************************")
        print("test --- test_plant_journal_model")
        print("*******************************")

# **************************
# BROWN THUMB VIEWS TEST 

    def test_search(self):
        with self.client as client:
            resp = client.get("/search?query=rose")
        
        self.assertIn("field rose", str(resp.data))
        self.assertIn("commonName", str(resp.data))
        self.assertIn("imageUrl", str(resp.data))
        self.assertEqual(resp.status_code, 200)

        print("*******************************")
        print("test --- test_search")
        print("*******************************")

    def test_get_user_plant(self):
        with self.client as client:
            resp = client.get(f"/plants/{self.user_plant_id}")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("water mint", str(resp.data))

        print("*******************************")
        print("test --- test_get_user_plant")
        print("*******************************")
    
    def test_get_plant_journal(self):
        with self.client as client:
            resp = client.get(f"/plants/{self.user_plant_id}/journal")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test title journal", str(resp.data))

        print("*******************************")
        print("test --- test_get_user_plant")
        print("*******************************")
    