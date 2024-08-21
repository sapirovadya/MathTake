import pytest
import app.modules.users.utils as utils

class TestSignupField:

    @classmethod
    def setup_method(cls):
        pass

    @classmethod
    def teardown_method(cls):
        pass

    def test_verify_name(self):
        # Valid names
        valid_first_name = "osnat"
        valid_full_name = "Sapir Oriya"
        assert utils.verify_name(valid_first_name) == True, f"Failed test_verify_name - input={valid_first_name} ,output=False"
        assert utils.verify_name(valid_full_name) == True, f"Failed test_verify_name - input={valid_full_name} ,output=False"

        # Invalid names
        invalid_name_with_num = "May123"
        invalid_name_with_spe = "Niv!" 
        invalid_empty_name = ""
        assert utils.verify_name(invalid_name_with_num) == False, f"Failed test_verify_name - input={invalid_name_with_num} ,output=True"
        assert utils.verify_name(invalid_name_with_spe) == False, f"Failed test_verify_name - input={invalid_name_with_num} ,output=True"
        assert utils.verify_name(invalid_empty_name) == False,  f"Failed test_verify_name - input={invalid_empty_name} ,output=True"

    def test_verify_phone_number(self):
        # Valid phone numbers
        valid_phone1 = "1234567890"
        valid_phone2 = "0987654321"
        assert utils.verify_phone_number(valid_phone1) == True, f"Failed test_verify_phone_number - input={valid_phone1} ,output=True"
        assert utils.verify_phone_number(valid_phone2) == True,  f"Failed test_verify_phone_number - input={valid_phone2} ,output=True"

        # Invalid phone numbers
        invlid_phone_short = "123456789"
        invlid_phone_long = "12345678901"
        invlid_phone_with_spe = "123-456-7890"
        invalid_phone_with_letters = "phone1234567"
        invalid_empty_phone = ""
        assert utils.verify_phone_number(invlid_phone_short) == False, f"Failed test_verify_phone_number - input={invlid_phone_short} ,output=True"
        assert utils.verify_phone_number(invlid_phone_long) == False, f"Failed test_verify_phone_number - input={invlid_phone_long} ,output=True"
        assert utils.verify_phone_number(invlid_phone_with_spe) == False, f"Failed test_verify_phone_number - input={invlid_phone_with_spe} ,output=True"
        assert utils.verify_phone_number(invalid_phone_with_letters) == False, f"Failed test_verify_phone_number - input={invalid_phone_with_letters} ,output=True"
        assert utils.verify_phone_number(invalid_empty_phone) == False, f"Failed test_verify_phone_number - input={invalid_empty_phone} ,output=True"

    def test_verify_good_password(self):
        # Valid passwords
        valid_pass1 = "Password1"
        valid_pass2 = "pass1234"
        valid_pass3 = "1234abc"
        assert utils.verify_password(valid_pass1) == True, f"Failed test_verify_good_password - input={valid_pass1} ,output=False"
        assert utils.verify_password(valid_pass2) == True, f"Failed test_verify_good_password - input={valid_pass2} ,output=False"
        assert utils.verify_password(valid_pass3) == True, f"Failed test_verify_good_password - input={valid_pass2} ,output=False"

        # Invalid passwords
        invalis_pass_short = "12345"
        invalis_pass_without_digit = "abcdef"
        invalis_pass_without_letters = "123456"
        assert utils.verify_password(invalis_pass_short) == False, f"Failed test_verify_good_password - input={invalis_pass_short} ,output=False"
        assert utils.verify_password(invalis_pass_without_digit) == False, f"Failed test_verify_good_password - input={invalis_pass_without_digit} ,output=False"  # no digits
        assert utils.verify_password(invalis_pass_without_letters) == False, f"Failed test_verify_good_password - input={invalis_pass_without_letters} ,output=False"  # no letters