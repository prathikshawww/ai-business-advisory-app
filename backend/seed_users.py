import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from werkzeug.security import generate_password_hash
from app import app
from database.models import db, User

with app.app_context():
    test_user = User(
        email="test@example.com",
        password=generate_password_hash("TestPassword123")
    )
    db.session.add(test_user)
    db.session.commit()
    print("Test user created:", test_user.email)