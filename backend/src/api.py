import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods=['GET'])
@requires_auth('get:drinks')
def _get_drinks(payload):
    drinks = Drink.query.all()
    data = [drink.short() for drink in drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify(
        {
            "success": True,
            "drinks": data
        }
    )

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def _get_drinks_details(payload):
    try:
        drinks = Drink.query.all()
        cust_drink = [rec.long() for rec in drinks]

        return jsonify({
            'success': True,
            'drinks': cust_drink
        }), 200
    except:
        abort(500)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def _create_drinks(payload):

    body = request.get_json()   

    if 'title' or 'recipe' not in body:
        abort(422)

    title = body['title']
    recipe = body['recipe']


    if not isinstance(recipe, list):
        abort(422)


    for ingredient in recipe:
        if not('color' in ingredient and 'name' in ingredient and 'parts' in ingredient):
            abort(422)

    recipe = json.dumps(recipe)

    try:
        add_drinks = Drink(title=title, recipe=recipe)
        add_drinks.insert()
        drinks = [add_drinks.long()]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def _update_drinks(payload, id):

    drink = Drink.query.get(id)

    if drink:
        try:

            body = request.get_json()

            title = body.get('title')
            recipe = body.get('recipe')

            if title:
                drink.title = title
            if recipe:
                drink.title = recipe

            drink.update()

            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        except:
            abort(422)
    else:
        abort(404)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def _delete_drinks(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
        }), 200
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
    "success": False,
    "error": 400,
    "message": "bad request"
    }), 400
    
@app.errorhandler(401)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Bad Request'
    }), 401

@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Unauthorized'
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
    "success": False,
    "error": 404,
    "message": "resource not found"
    }), 404

@app.errorhandler(405)
def not_found(error):
    return jsonify({
    "success": False,
    "error": 405,
    "message": "method not allowed"
    }), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
    "success": False,
    "error": 422,
    "message": "unprocessable"
    }), 422

@app.errorhandler(500)
def  bad_request(error):
    return jsonify({
    "success": False,
    "error": 500,
    "message": "internal error server"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code