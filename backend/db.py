from pymongo import MongoClient
from bson import ObjectId
import json

with open("config.json", "r") as f:
    config = json.load(f)
    


class PressReleaseDatabase:
    def __init__(self, db_uri=config.get("mongodb_uri", "mongodb://127.0.0.1:27017/"), db_name="press_releases"):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.press_releases_collection = self.db["releases"]
        self.users_collection = self.db["users"]

    def save_press_release(self, data):
        try:
            self.press_releases_collection.insert_one(data)
        except Exception as e:
            print(f"Error saving press release to database: {e}")
        
    def get_press_release(self, id):
        press_release = self.press_releases_collection.find_one({"_id": ObjectId(id)})
        if press_release:
            return press_release
        else:
            return None

    def get_press_releases(self):
        all_press_releases = list(self.press_releases_collection.find({}))
        return all_press_releases

    def save_user(self, username, password, email):
        try:
            self.users_collection.insert_one({"username": username, "password": password, "email": email})
        except Exception as e:
            print(f"Error saving user to database: {e}")
            
    def confirm_user(self, username, password):
        user = self.users_collection.find_one({"username": username, "password": password})
        if user:
            return True
        else:
            return False
        
    def does_user_exist(self, username):
        user = self.users_collection.find_one({"username": username})
        return True if user else False