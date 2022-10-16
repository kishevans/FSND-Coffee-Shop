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

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# Endpoint to handle GET requests for drinks and return in shortform
# representaion


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks_list = Drink.query.all()
        drinks = []
        for drink in drinks_list:
            drinks.append(drink.short())
            # return 'drink'
            return jsonify({
                'success': True,
                "drinks": drinks
            })
    except BaseException:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# Endpoint to handle GET requests for drinks-details and return in
# longform representaion


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    try:
        drinks_list = Drink.query.all()
        drinks = []
        for drink in drinks_list:
            drinks.append(drink.long())
            return jsonify({
                'success': True,
                'drinks': drinks
            })
    except BaseException:
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
# Endpoint to handle POST requests for drinks and add in longform
# representaion to database


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()
    new_title = body.get('title')
    new_recipe = json.dumps(body.get('recipe'))

    drink = Drink()
    drink.title = new_title
    drink.recipe = new_recipe
    #drink = Drink(title=new_title,recipe=new_recipe)

    drink.insert()
    drink = [drink.long()]

    return jsonify({
        'success': True,
        'drink': drink
    })


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
# Endpoint to handle PATCH request to update drink details in the database
# and return drink in longform


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    body = request.get_json()
    new_title = body.get('title')
    new_recipe = json.dumps(body.get('recipe'))  # convert dictionary to string
    if new_title:
        drink.title = new_title
    elif new_recipe:
        drink.recipe = new_recipe
    drink.update()
    drink = [drink.long()]

    return jsonify({
        'success': True,
        'drinks': drink
    })


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
# Endpoint to handle DELETE requests to delete selected item based on its
# id in te database and return deleted id


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    drink.delete()
    id = drink.id
    return jsonify({
        'success': True,
        "delete": id
    })


# Error Handling
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


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
# Error handlers for all expected errors
# Error handlers for 404 errors - resource not found


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=80, debug=True)
