import os
import yaml


class Config:
    # Load configuration from YAML file
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    SECRET_KEY = config.get("SECRET_KEY") or "secret_key"
    MONGO_URI = config.get("MONGO_URI")
    MONGO_DBNAME = config.get("MONGO_DBNAME")
    MAIL_SERVER = config.get("MAIL_SERVER")
    MAIL_PORT = config.get("MAIL_PORT") or 587
    MAIL_USE_TLS = config.get("MAIL_USE_TLS", True)
    MAIL_USERNAME = config.get("MAIL_USERNAME")
    MAIL_PASSWORD = config.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = config.get("MAIL_DEFAULT_SENDER") or MAIL_USERNAME