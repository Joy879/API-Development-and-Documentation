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
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization, true')
        response.headers.add(
            'Access-Control-Allow-Headers',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response
# ----------------------------------------------------------------------------#
# Api Endpoints
# ----------------------------------------------------------------------------#

#  Categories
#  ----------------------------------------------------------------

    @app.route("/categories")
    def get_categories():
        """
        Makes a query to the category table and
        displays the results as a dictionary
        """
        categories = Category.query.all()
        all_categories = [category.format() for category in categories]

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {
                category['id']: category['type'] for category in all_categories
                }
        })
#  Questions
#  ----------------------------------------------------------------#

    @app.route('/questions')
    def get_questions():
        """
        Queries the questions table and returns a list of questions,
         number of total questions, current category, categories
        """
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
            'categories': {
                category['id']: category['type'] for category in all_categories
                },
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
#  Post or Search for Questions
#  ----------------------------------------------------------------

    @app.route("/questions", methods=["POST"])
    def post_or_search_question():
        """
        Combining search and post under one endpoint
        """
        body = request.get_json()

        new_question = body.get('question', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        new_answer = body.get('answer', None)
        search_term = body.get('searchTerm', None)

        try:
            """
            If searchterm is submitted,
            find and return all questions with the search term
            """
            if search_term:
                select_questions = (
                    Question.query.order_by(Question.id).filter(
                        Question.question.ilike("%{}%".format(search_term))))

                # Paginate the questions
                current_questions = paginate_questions(
                    request, select_questions)

                return jsonify({
                        'success': True,
                        'questions': current_questions,
                        'total_questions': len(select_questions.all())
                        })
            else:
                """
                Request is determined as a request
                to add a question since it does not contain a searchterm
                in the json request body
                """
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty)
                question.insert()

                questions = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, questions)

                return jsonify({
                    'questions': current_questions,
                    'totalQuestions': len(Question.query.all()),
                    'currentCategory': 'none'
                })

        except:
            abort(404)


#  Search for questions based on category
#  ----------------------------------------------------------------

    @app.route("/categories/<int:category_id>/questions")
    def search_category(category_id):
        """
        Search for questions based on the category
        """
        category = Category.query.filter_by(id=category_id).one_or_none()

        if category is None:
            abort(404)

        if category is not None:
            questions = Question.query.filter_by(
                category=str(category_id)).all()

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

        try:
            if category['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(
                    Question.category == category['id']).all()

            len_questions = len(questions)

            random_question = random.choice(questions)

            if len(previous_questions) == len_questions:
                return jsonify({'success': True})
            else:

                return jsonify({'success': True,
                               'question': random_question.format()})
        except:
            abort(404)
#  ----------------------------------------------------------------#
#  Error Handlers
#  ----------------------------------------------------------------#

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                "success": False,
                "error": 400,
                "message": "bad request"}),
            400,
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({
                "success": False,
                "error": 405,
                "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify({
                "success": False,
                "error": 500,
                "message": "internal server error"}),
            500,
        )

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

    return app
