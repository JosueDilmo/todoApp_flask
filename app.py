from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from functools import wraps

# Creating an instance of Flask
app = Flask(__name__)

# Creating an instance of Flask_Bcrypt
bcrypt = Bcrypt(app)

# Setting up the MongoDB database connection
client = MongoClient('mongodb+srv://admin:Password1@cluster0.kjtwkrj.mongodb.net/?retryWrites=true&w=majority')

# Setting up the database and collections
db = client.mydb
todos = db.todos
users = db.users

# Setting up the app secret key for sessions
app.secret_key = 'Something very secret!'


# POST new todos on the database and retrieve all todos from the database.
# Index is using the index.html template.
@app.route('/todo', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        # Get the content, degree of priority, and due date from the form
        content = request.form['content']
        degree = request.form['degree']
        due_date = request.form['due_date']

        # Insert the new todos into the todos collection
        todos.insert_one({'content': content, 'degree': degree, 'due_date': due_date})

        # Redirect to the index page to show the updated list of todos
        return redirect(url_for('index'))

    # Find all todos in the database
    all_todos = todos.find()

    # Render the index.html template with the todos data
    return render_template('index.html', todos=all_todos)


# Delete the todo with the given id from the Atlas database.
@app.post('/<id>/delete/')
def delete(id):
    # Delete the todos from the todos collection using its ID
    todos.delete_one({"_id": ObjectId(id)})

    # Redirect to the index page to show the updated list of todos
    return redirect(url_for('index'))


# Login required decorator to restrict access to certain pages.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            # Redirect the user to the login page if they're not logged in
            return redirect(url_for('login', next=request.url))

        # Call the original function if the user is logged in
        return f(*args, **kwargs)

    return decorated_function


# Login page when "localhost" is accessed.
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the username and password from the login form
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the user in the users collection
        user = users.find_one({'username': username})

        if user is None:
            # Return an error message if the username doesn't exist in the database
            return 'Invalid username or password'

        if bcrypt.check_password_hash(user['password'], password):
            # Set the user session if the password is correct
            session['user'] = username
            # Redirect to the index page to show the list of todos
            return redirect(url_for('index'))
        # Return an error message if the password is incorrect
        return 'Invalid username or password'
    # Render the login.html template if the request is a GET request
    return render_template('login.html')


# Template render for the registration form
@app.route('/register')
def register_form():
    return render_template('register.html')


# Register user by username and password
# handle the submission of the registration form
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    # check if the username is already registered
    user_registered = users.find_one({'username': username})

    # if the users does not exit, create it
    if user_registered is None:
        passwordHash = bcrypt.generate_password_hash(password).decode('utf-8')

        # add document to the database
        users.insert_one({'username': username, 'password': passwordHash})

        # redirect to login page
        return redirect(url_for('login'))

    # if username is already registered, do not register
    return 'Username already registered!'.encode('utf-8')


# run app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
