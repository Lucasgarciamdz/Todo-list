import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import db, Todo, app  # noqa: E402


class TestTodoApp(unittest.TestCase):
    def setUp(self):
        # Set up a test database
        self.app = app.test_client()
        with app.app_context():
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
            app.config['TESTING'] = True
            db.create_all()

    def tearDown(self):
        # Clean up the test database
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page(self):
        # Test the home page
        with app.app_context():
            response = self.app.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'To Do App', response.data)

    def test_add_task(self):
        with app.app_context():
            response = self.app.post('/add', data=dict(task='Test Task'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Task', response.data)
            task_title = 'Test Task'
            # Check if task exists in the database
            task_in_db = Todo.query.filter_by(task=task_title).first()
            self.assertIsNotNone(task_in_db)
            self.assertEqual(task_in_db.task, task_title)

    def test_update_task(self):
        with app.app_context():
            # Add a new task to the database
            self.app.post('/add', data={'task': 'Test Task', 'completed': False})
            task = Todo.query.filter_by(task='Test Task').first()
            self.app.get(f'/update_status/{task.id}')
            updated_task = Todo.query.get(task.id)
            self.assertTrue(updated_task.completed)

    def test_edit_task(self):
        with app.app_context():
            self.app.post('/add', data={'task': 'Test Task', 'completed': False})
            task = Todo.query.filter_by(task='Test Task').first()
            self.app.post(f'/edit/{task.id}', data={'new_title': 'New Test Task'})
            edited_task = Todo.query.get(task.id)
            assert edited_task.task == 'New Test Task'


if __name__ == '__main__':
    unittest.main()
