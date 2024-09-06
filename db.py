from pymongo.collection import Collection
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Dict, Optional, Any, List
from database_manager import DatabaseManager

class PressReleaseDatabase:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.db = self.db_manager.get_db()
        self.press_releases_collection: Collection = self.db["releases"]
        self.users_collection: Collection = self.db["users"]

    def save_press_release(self, data: Dict[str, Any]) -> str:
        """
        Save a new press release to the database.
        """
        try:
            result = self.press_releases_collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving press release to database: {e}")
            return ""

    def get_press_release(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a press release by its ID.
        """
        try:
            release = self.press_releases_collection.find_one({"_id": ObjectId(id)})
            if release:
                return release
            else:
                print(f"No press release found with id: {id}")
                return None
        except Exception as e:
            print(f"Error retrieving press release from database: {e}")
            return None

    def get_press_releases(self) -> List[Dict[str, Any]]:
        """
        Retrieve all press releases from the database.
        """
        try:
            return list(self.press_releases_collection.find({}))
        except Exception as e:
            print(f"Error retrieving press releases from database: {e}")
            return []

    def save_user(self, username: str, password: str, email: str) -> bool:
        """
        Save a new user to the database with a hashed password.
        """
        try:
            hashed_password = generate_password_hash(password, method='sha256')
            self.users_collection.insert_one({
                "username": username,
                "password": hashed_password,
                "email": email
            })
            return True
        except Exception as e:
            print(f"Error saving user to database: {e}")
            return False

    def confirm_user(self, username: str, password: str) -> bool:
        """
        Confirm user credentials.
        """
        try:
            user = self.users_collection.find_one({"username": username})
            if user and check_password_hash(user["password"], password):
                return True
            return False
        except Exception as e:
            print(f"Error confirming user: {e}")
            return False

    def does_user_exist(self, username: str) -> bool:
        """
        Check if a user already exists in the database.
        """
        try:
            exists = self.users_collection.find_one({"username": username}) is not None
            return exists
        except Exception as e:
            print(f"Error checking if user exists: {e}")
            return False
