# Imports
# ----------------------------------------------------------------------------
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category
# ----------------------------------------------------------------------------#
# Pagination
# ----------------------------------------------------------------------------#
QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    """ Paginates the questions to be viewed 10 per page """
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    paginated_questions = questions[start:end]

    return paginated_questions
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        """ Use the after_request decorator to set Access-Control-Allow"""
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
# ----------------------------------------------------------------------------#
# Api Endpoints
# ----------------------------------------------------------------------------#

#  Categories
#  ----------------------------------------------------------------

    @app.route("/categories")
    def get_categories():
        """Makes a query to the category table and displys the results as a dictionary"""
        categories = Category.query.all()
        all_categories = [category.format() for category in categories]

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {category['id']: category['type'] for category in all_categories}
        })
#  Questions
#  ----------------------------------------------------------------#

    @app.route('/questions')
    def get_questions():
        """Queries the questions table and returns a list of questions, number of total questions, current category, categories"""
        questions = Question.query.order_by(Question.id).all()
        paginated_questions = paginate_questions(request, questions)
        categories = Category.query.all()
        all_questions = [question.format() for question in questions]
        all_categories = [category.format() for category in categories]

        if len(paginated_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'categories': {category['id']: category['type'] for category in all_categories},
            'current_category': None,
            'total_questions': len(all_questions)
        })

#  Delete Questions
#  ----------------------------------------------------------------

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """Delete existing questions"""
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(400)

            question.delete()
            return jsonify({
                'success': True,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)
#  Post Question
#  ----------------------------------------------------------------

    @app.route("/questions", methods=["POST"])
    def add_question():
        """Create a new question defined by the user"""
        body = request.get_json()
        try:
            newQuestion = Question(question=body['question'], answer=body['answer'], category=body['category'], difficulty=body['difficulty'])
            newQuestion.insert()

            return jsonify({
                'success': True,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

#  Search for questions
#  ----------------------------------------------------------------
    @app.route("/questions/search", methods=['POST'])
    def search_questions():
        """Search for any question using strings/substrings"""
        searchTerm = request.get_json()
        questions = Question.query.filter(Question.question.ilike("%"+searchTerm["searchTerm"]+"%")).all()

        if questions is None:
            abort(404)

        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': None
        })

#  Search for questions based on category
#  ----------------------------------------------------------------
    @app.route("/categories/<int:category_id>/questions")
    def search_category(category_id):
        """Search for questions based on the category"""
        category = Category.query.filter_by(id=category_id).one_or_none()

        if category is None:
            abort(404)

        if category is not None:
            questions = Question.query.filter_by(category=str(category_id)).all()

        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })
#  Quizzes
#  ----------------------------------------------------------------

    @app.route("/quizzes", methods=['POST'])
    def quizzes():
        """Endpoint to get questions to play the quiz."""
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        category = body.get('quiz_category')

        if category is None:
            abort(404)

        if previous_questions is None:
            abort(404)

        questions = None
        if (category['id'] == 0):
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter(Question.id.notin_(previous_questions), Question.category == category['id']).all()

        total_questions = len(questions)

        if total_questions:
            question = random.choice(questions)
            return jsonify({'success': True, 'question': question.format()})
#  ----------------------------------------------------------------#
#  Error Handlers
#  ----------------------------------------------------------------#

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({
                "success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

    return app
