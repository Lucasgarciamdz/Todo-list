from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from

# Create an instance of the Flask class with the path for template and statics
app = Flask(__name__, template_folder='../templates', static_folder='../static')
swagger_config = Swagger.DEFAULT_CONFIG
swagger_config['swagger_ui'] = True
swagger_config["swagger_version"] = "3.0"
# General config for swagger, create the instance of the Swagger class and pass the config and path of the swaggger.yml file # noqa: E501
swagger = Swagger(app, config=swagger_config, template_file='swagger.yml')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
# Create an instance of the SQLAlchemy class and db uri config
db = SQLAlchemy(app)


# Create the database using db.Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False)


# First route, it renders the homepage
@app.route("/")
def todo_list():
    todo_list = Todo.query.all()
    return render_template("home.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
@swag_from("swagger.yml")
def add_task():
    task = request.form.get("task")
    new_todo = Todo(task=task, completed=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("todo_list"))


@app.route("/update_status/<int:task_id>")
def update_status(task_id):
    todo = Todo.query.filter_by(id=task_id).first()
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("todo_list"))


@app.route("/delete/<int:task_id>")
def delete(task_id):
    todo = Todo.query.filter_by(id=task_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("todo_list"))


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    todo = Todo.query.filter_by(id=task_id).first()
    todo.task = request.form.get('new_title')
    db.session.commit()
    return redirect(url_for("todo_list"))


with app.app_context():
    db.create_all()
