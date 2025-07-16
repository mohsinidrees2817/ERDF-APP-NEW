import os
import streamlit as st
import bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(st.secrets["MONGO_URI"])
db = client["erdf_auth"]
users = db["users"]


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)


def create_user(email, password):
    if users.find_one({"email": email}):
        return False
    hashed = hash_password(password)
    users.insert_one({"email": email, "password": hashed})
    return True


def login_user(email, password):
    user = users.find_one({"email": email})
    if not user:
        return False
    if check_password(password, user["password"]):
        return True
    return False
