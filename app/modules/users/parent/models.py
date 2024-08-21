from flask import Flask 
from modules.users.models import User

class Parent(User):
    def signup(self, data) :
        parent = User().signup(data)
        return parent

 