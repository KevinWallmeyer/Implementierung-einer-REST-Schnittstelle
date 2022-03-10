
from csv import list_dialects
from pickle import FALSE
import uuid 

from flask import Flask, request, jsonify, abort

# initialize Flask server
app = Flask(__name__)

# create unique id for lists, users, entries
user_id_bob = uuid.uuid4()
user_id_alice = uuid.uuid4()
user_id_eve = uuid.uuid4()

todo_list_1_id = '1318d3d1-d979-47e1-a225-dab1751dbe75'
todo_list_2_id = '3062dc25-6b80-4315-bb1d-a7c86b014c65'
todo_list_3_id = '44b02e00-03bc-451d-8d01-0c67ea866fee'

todo_1_id = uuid.uuid4()
todo_2_id = uuid.uuid4()
todo_3_id = uuid.uuid4()
todo_4_id = uuid.uuid4()

# define internal data structures with example data
user_list = [
    {'id': user_id_bob, 'name': 'Bob'},
    {'id': user_id_alice, 'name': 'Alice'},
    {'id': user_id_eve, 'name': 'Eve'},
]
todo_lists = [
    {'id': todo_list_1_id, 'name': 'Einkaufsliste'},
    {'id': todo_list_2_id, 'name': 'Arbeit'},
    {'id': todo_list_3_id, 'name': 'Privat'},
]
todos = [
    {'id': todo_1_id, 'name': 'Milch', 'description': '', 'list': todo_list_1_id, 'user': user_id_bob, "done": False},
    {'id': todo_2_id, 'name': 'Arbeitsblätter ausdrucken', 'description': '', 'list': todo_list_2_id, 'user': user_id_alice, "done": False},
    {'id': todo_3_id, 'name': 'Kinokarten kaufen', 'description': '', 'list': todo_list_3_id, 'user': user_id_eve, "done": False},
    {'id': todo_3_id, 'name': 'Eier', 'description': '', 'list': todo_list_1_id, 'user': user_id_eve, "done": False},
]

# add some headers to allow cross origin access to the API on this server, necessary for using preview in Swagger Editor!
@app.after_request
def apply_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# define endpoint for getting and deleting existing todo lists
@app.route('/list/<list_id>', methods=['GET', 'DELETE', 'POST'])
def handle_list(list_id):
    # find todo list depending on given list id
    list_item = None
    for l in todo_lists:
        if str(l['id']) == str(list_id): #for some reason I have to convert the ids to strings, otherwise the IF-clause does not work with UUIDs
            list_item = l
            break

    # if the given list id is invalid, return status code 404
    if not list_item:
        abort(404)

    if request.method == 'GET':
        # find all todo entries for the todo list with the given id
        print('Returning todo list...')
        return jsonify([i for i in todos if i['list'] == list_id])

    if request.method == 'DELETE':
        # delete list with given id
        print('Deleting todo list...')
        todo_lists.remove(list_item)
        return '', 200
    
    if request.method == 'POST':
        #rename the list
        # bare minimum for JSON:
        #       {
        #       "name": ""
        #       }

        # make JSON from POST data (even if content type is not set correctly)
        new_name_for_list = request.get_json(force=True)
        print('Got new name for list: {}'.format(new_name_for_list))
        list_item['name'] = new_name_for_list['name']
        return jsonify(list_item), 200


# define endpoint for adding a new list
@app.route('/list/', methods=['POST'])
def add_new_list():
    #Bare minimum for JSON:
    #       {
    #       "name": ""
    #       }
    # make JSON from POST data (even if content type is not set correctly)
    new_list = request.get_json(force=True)
    print('Got new list to be added: {}'.format(new_list))
    # create id for new list, save it and return the list with id
    new_list['id'] = uuid.uuid4()
    todo_lists.append(new_list)
    return jsonify(new_list), 200


# define endpoint for adding a new entry to a list
@app.route('/list/<list_id>/entry/', methods=['POST'])
def add_new_entry(list_id):
    list_item = None
    for l in todo_lists:
        if str(l['id']) == str(list_id):
            list_item = l
            break

    # if the given list id is invalid, return status code 404
    if not list_item:
        abort(404)
    else:
        #Bare minimum for JSON:
        #   {
        #       "description": "",
        #       "name": "",
        #       "user": "~valid_id~" <-- the id has to be in the user list
        #   }
        # make JSON from POST data (even if content type is not set correctly)
        new_entry = request.get_json(force=True)
        
        # find user of the new entry depending on given id
        user_of_new_entry = None
        for u in user_list:
            if str(u['id']) == str(new_entry['user']):
                user_of_new_entry = u
                break
                    
        if not user_of_new_entry:
            abort(404)

        print('Got new entry to be added: {}'.format(new_entry))

        # create id for new list, save it and return the list with id
        new_entry['id'] = uuid.uuid4()
        new_entry['list'] = list_id
        new_entry['done'] = False
        
        todos.append(new_entry)
        return jsonify(new_entry), 200


# define endpoint for updating and deleting an entry of a list
@app.route('/list/<list_id>/entry/<entry_id>', methods=['POST', 'DELETE'])
def update_entry(list_id, entry_id):
    #find the list
    wanted_list = None
    for l in todo_lists:
        if str(l['id']) == str(list_id):
            wanted_list = l
            break
    
    #find the entry
    wanted_entry = None
    for e in todos:
        if str(e['id']) == str(entry_id):
            wanted_entry = e
            break
    
    if not wanted_list or not wanted_entry:
        abort(404)

    #updates the entry     
    if request.method == 'POST':
        #Bare minimum for the JSON:
        #       {
        #       "description": "", <-- If you want to remove the description, you have to enter a space here("description": " ")
        #       "done": "", <-- either has to be "true" or "false" without quotation marks if you want to change it      
        #       "name": "",
        #       "user": "" <-- if you want to change the user, make sure that the user's id is valid
        #       }
        # make JSON from POST data (even if content type is not set correctly)
        updated_entry = request.get_json(force=True)
        for x in todos:
            if str(x['id']) == str(wanted_entry['id']) and str(x['list']) == str(wanted_list['id']):

                if updated_entry['description'] != "":
                    x['description'] = updated_entry['description']               

                if updated_entry['name'] != "":
                    x['name'] = updated_entry['name']

                if str(updated_entry['user']) != "":
                    # find user depending on given id
                    user_to_update = None
                    for u in user_list:
                        if str(u['id']) == str(updated_entry['user']):
                            user_to_update = u
                            break
                    
                    if not user_to_update:
                        abort(404)
                    else:
                        x['user'] = updated_entry['user']

                if updated_entry['done'] != "":
                    x['done'] = updated_entry['done']

                return jsonify(updated_entry), 200
    
    #deletes the entry
    if request.method == 'DELETE':
        for y in todos:
            if str(y['id']) == str(wanted_entry['id']) and str(y['list']) == str(wanted_list['id']):
                todos.remove(y)
                return '', 200
    
    
# define endpoint for getting all users and adding new ones
@app.route('/users/', methods=['GET', 'POST'])
def handle_users():
    #return all users
    if request.method == 'GET':
        return jsonify(user_list)

    #add a new user
    if request.method == 'POST':
        #Bare minimum for the JSON:
        #       {    
        #       "name": ""
        #       }
        # make JSON from POST data (even if content type is not set correctly)
        new_user = request.get_json(force=True)
        print('Got new user to be added: {}'.format(new_user))
        # create id for new user, save it and return the user with id
        new_user['id'] = uuid.uuid4()
        user_list.append(new_user)
        return jsonify(new_user), 200


# define endpoint for deleting a user
@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # find user depending on given id
    user_to_delete = None
    for u in user_list:
        if str(u['id']) == str(user_id):
            user_to_delete = u
            break
    
    if not user_to_delete:
        abort(404)
    else:
        #delete user
        print("Deleting user... ")
        user_list.remove(user_to_delete)
        return '', 200

# define endpoint for getting all lists
@app.route('/lists', methods=['GET'])
def get_all_lists():
    return jsonify(todo_lists)


if __name__ == '__main__':
    # start Flask server
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

