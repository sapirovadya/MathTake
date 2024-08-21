import re

def verify_name(name):
    return bool(re.fullmatch(r'[A-Za-z]+(?: [A-Za-z]+)*', name))

def verify_phone_number(phone):
    print(f"\nphone = {phone}\ntype={type(phone)}\n")
    return bool(re.fullmatch(r'\d{10}', phone))

def verify_password(password):
    if len(password) < 6:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit