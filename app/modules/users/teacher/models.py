from flask import Flask 
from modules.users.models import User

class Teacher(User):
    def signup(self, data) :
        teacher = User().signup(data)
        return teacher

 