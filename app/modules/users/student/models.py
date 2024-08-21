from flask import Flask 
from modules.users.models import User

class Student(User):
    def signup(self, data) :
        student = User().signup(data)
        student["parent_email"] = data["parent_email"]

        return student

 