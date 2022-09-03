import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category
from settings import TEST_DB_NAME, DB_PASSWORD, DB_USER


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = TEST_DB_NAME
        self.database_account = DB_USER
        self.database_password = DB_PASSWORD
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.database_account, self.database_password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

# Failure question
    def fail_questions_put(self):
        res = self.client().put('/questions')

        self.assertEqual(res.status_code, 405)

    def fail_questions_delete(self):
        res = self.client().delete('/questions')
        self.assertEqual(res.status_code, 405)

    def fail_questions_patch(self):
        res = self.client().patch('/questions')
        self.assertEqual(res.status_code, 405)

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # Failure category
    def fail_category_post(self):
        res = self.client().post('/categories')
        self.assertEqual(res.status_code, 405)

    def fail_category_put(self):
        res = self.client().put('/categories')
        self.assertEqual(res.status_code, 405)

    def fail_category_post_delete(self):
        res = self.client().delete('/categories')
        self.assertEqual(res.status_code, 405)

    def fail_category_post_patch(self):
        res = self.client().patch('/categories')
        self.assertEqual(res.status_code, 405)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000", json={"difficulty": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # Delete a different question in each attempt
    def test_delete_question(self):
        res = self.client().delete("/questions/6")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_fail_to_delete_question(self):
        res = self.client().get("/questions/500")
        self.assertEqual(res.status_code, 405)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        res = self.client().post("/questions/search", json=({'searchTerm': 'new'}))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def fail_to_test_search_questions(self):
        res = self.client().post("/search", json=({'searchTerm': 'new'}))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_quizzes(self):
        res = self.client().post("/quizzes", json=({'previous_questions': [], 'quiz_category': {'id': '1', 'type': 'Sports'}}))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_fail_to_test_quizzes(self):

        res = self.client().post("/quizzes", json={})
        self.assertEqual(res.status_code, 404)

    def test_search_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data["current_category"])

    def test_fail_test_search_category(self):
        res = self.client().post("/quizzes", json={})
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
