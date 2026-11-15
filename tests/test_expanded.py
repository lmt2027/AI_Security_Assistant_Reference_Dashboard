import tempfile
import unittest
from pathlib import Path
import database
from event_detection import analyze_database_events

class ExpandedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = database.DB_PATH
        database.DB_PATH = Path(self.tmp.name) / 'test.db'
        database.create_database()
        database.create_event_tables()
        database.create_response_tables()

    def tearDown(self):
        database.DB_PATH = self.old
        self.tmp.cleanup()

    def test_new_detection_rules(self):
        database.seed_security_events()
        found = analyze_database_events()
        titles = [r[1] for r in found]
        self.assertIn('Possible Password Attack', titles)
        self.assertIn('Multiple Accounts Targeted From One Source', titles)
        self.assertIn('Software Update Pending', titles)
        self.assertIn('New Account Requires Review', titles)
        self.assertEqual(analyze_database_events(), [])

    def test_simulated_response_plan(self):
        database.seed_demo_alerts()
        ident = database.add_response_action(1, 'Review access', 'Test note')
        self.assertEqual(database.get_response_actions()[0][3], 'Planned')
        self.assertEqual(database.update_response_action(ident, 'Completed', 'Checked'), 1)
        self.assertEqual(database.get_response_actions()[0][3], 'Completed')

    def test_invalid_response_status(self):
        with self.assertRaises(ValueError):
            database.update_response_action(1, 'Actually blocked', '')

if __name__ == '__main__':
    unittest.main()
