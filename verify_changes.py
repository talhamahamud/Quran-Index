import unittest
from app import app, db, Post

class TestIndexPage(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory DB for test safety, 
        # BUT here we actually want to test against the REAL db to see if migration worked. 
        # However, for a quick check without messing things up, I will just inspect the real DB file via the app context 
        # or just rely on the fact that I just ran the migration on site.db.
        
        # Let's use the actual app config to test against the real DB content
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_index_renders_posts(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        
        # Check for titles that we migrated
        expected_titles = [
            "(১৪) সূরা ইব্রাহিম",
            "(১৫) সূরা আল-হিজর",
            "(১৬) আন্ নাহল",
            "(১৮) আল কাহফ",
            "(১৯) মারয়াম"
        ]
        
        for title in expected_titles:
            self.assertIn(title, content)
            print(f"Verified title present: {title}")

        # Ensure random other posts are NOT present (assuming 'Jhanna' was the offender)
        # However without creating it first we can't be sure, but we can check if only 5 sections are rendered?
        # Let's count occurrences of "main-section"
        section_count = content.count('class="main-section"')
        print(f"Number of sections found: {section_count}")
        self.assertEqual(section_count, 5, "Should ONLY have 5 sections")

    def test_edit_button_presence(self):
        # Must be logged in to see edit button
        with self.app as c:
            # Login first (mocking login handling or just setting session)
            # Since we didn't mock login properly in setUp, let's login via route
            c.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
            response = c.get('/')
            content = response.data.decode('utf-8')
            if "[Edit]" in content:
                 print("Edit button verified present for admin")
            else:
                 self.fail("Edit button missing for admin")

if __name__ == '__main__':
    unittest.main()
