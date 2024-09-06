from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict, Union
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(
        self,
        user_id: Union[str, ObjectId],
        username: str,
        password_hash: str,
        email: Optional[str] = None,
        global_admin: bool = False,
        confirmed: bool = False,
    ):
        self.id = str(user_id)
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.global_admin = global_admin
        self.confirmed = confirmed

    @staticmethod
    def from_db(user_doc: Dict) -> 'User':
        """
        Create a User instance from a database document.
        """
        return User(
            user_id=user_doc["_id"],
            username=user_doc["username"],
            email=user_doc.get("email"),
            password_hash=user_doc["password_hash"],
            global_admin=user_doc.get("global_admin", False),
            confirmed=user_doc.get("confirmed", False),
        )

    def check_password(self, password: str) -> bool:
        """
        Verify the provided password against the stored password hash.
        """
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_user(username: str, password: str, email: Optional[str] = None) -> Dict:
        """
        Create a new user dictionary with a hashed password.
        """
        password_hash = generate_password_hash(password)
        return {
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "global_admin": False,
            "confirmed": False,
        }

    def change_password(self, db, new_password: str) -> None:
        """
        Change the user's password and update the database.

        :param db: The database connection
        :param new_password: The new password to be set
        """
        new_password_hash = generate_password_hash(new_password)
        self.password_hash = new_password_hash

        # Update the password hash in the database
        db.users.update_one(
            {"_id": ObjectId(self.id)}, {"$set": {"password_hash": self.password_hash}}
        )
        print("Password updated successfully.")
