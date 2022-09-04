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
@app.route('/drinks', methods=['GET'])
def drinks():
    """
    Public permission
    This API fetches all drinks with a short description
    Return the drinks array or the error handler
    """
    try:
        drinks = Drink.query.all()
        if drinks is None:
            abort(404)
        all_drinks = []
        for drink in drinks:
            all_drinks.append(drink.short())
        return jsonify({"success":True,"drinks": all_drinks}), 200
    except:
        abort(500)



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
def get_drink_detail(payload):
    try:
        drinks = Drink.query.all()
        if drinks is None:
            abort(404)
        all_drinks = []
        for drink in drinks:
            all_drinks.append(drink.long())
        return jsonify({'success': True,'drinks': all_drinks}), 200
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
def create_drink(payload):
    data = request.get_json()
    if data is None or "recipe" not in data or "title" not in data:
        abort(404)
    try:
        recipe = data["recipe"]
        title = data["title"]
        print (recipe)
        if not isinstance(recipe, list):
            recipe = [recipe]
        recipe_json = json.dumps(recipe)
        print (recipe_json)
        drink = Drink(title=title, recipe=recipe_json)
        drink.insert()
        return jsonify({'success': True, 'drinks': drink.long()})
    except:
        abort(400)

    
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
def update_drink(payload, id):
    data = request.get_json()
    if data is None or "recipe" not in data or "title" not in data:
        abort(404)
    try:
        drink = Drink.query.get(Drink.id == id)
        title = data["title"]
        recipe = data["recipe"]
        drink.title = title
        if not isinstance(recipe, list):
            recipe = [recipe]
        recipe_json = json.dumps(recipe)
        drink.recipe = recipe_json
        drink.update()
        return jsonify({'success': True, 'drinks': drink.long()}), 200
    except:
        abort(400)

   


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

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({'success': True,'delete': id})
    except:
        abort(400)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404,"message": "resource not found"}), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"success": False,"error": 401,"message": 'Not authorized'}), 401


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    message =  error.error["description"]
    code = error.status_code
    return jsonify({"success": False,"error": code,"message": message}), code
