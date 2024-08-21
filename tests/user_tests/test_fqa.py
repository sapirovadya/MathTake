import unittest
import os

class TestFAQPage(unittest.TestCase):

    def test_faq_page_exists(self):
        """Test if the FQA.html file exists in the correct directory."""
        faq_path = os.path.join(os.getcwd(), 'app', 'templates', 'FQA.html')
        self.assertTrue(os.path.exists(faq_path), f"FQA.html file does not exist at {faq_path}")

    def test_faq_content_exists(self):
        """Test if specific FAQ content is present in the FQA.html file."""
        faq_path = os.path.join(os.getcwd(), 'app', 'templates', 'FQA.html')
        with open(faq_path, 'r', encoding='utf-8') as file:
            content = file.read()
            self.assertIn('Frequently Asked Questions', content, "'Frequently Asked Questions' not found in FQA.html")
            self.assertIn('What is MathTake?', content, "'What is MathTake?' not found in FQA.html")

if __name__ == '__main__':
    unittest.main()