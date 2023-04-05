from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId


# instance for flask
app = Flask(__name__)

# database in Atlas MongoDB
client = MongoClient('mongodb+srv://admin:Password1@cluster0.kjtwkrj.mongodb.net/?retryWrites=true&w=majority')

# Variables
db = client.mydb
todos = db.todos


# Post new todos on the database and retrieve all todos from the database
# Index is using the index.html template
@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method=='POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.insert_one({'content': content, 'degree': degree})
        return redirect(url_for('index'))

    all_todos = todos.find()
    return render_template('index.html', todos=all_todos)


# Delete the todos on the Atlas database
@app.post('/<id>/delete/')
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
