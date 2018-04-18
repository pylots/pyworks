# -*- coding: utf-8 -*-
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_restful import Api, Resource

from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user

# create our little application :)
app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(object):

    def __init__(self, *args, **kw):
        self.id = kw['id']
        self.name = kw['name']
        self.password = kw['password']
        self.email = kw['email']
        self.urole = kw['urole']
        self.ulevel = kw['ulevel']

    @staticmethod
    def get(userid):
        if userid < len(userlist):
            return userlist[int(userid)]

        return None

    @staticmethod
    def lookup(username):
        for user in userlist:
            if user.name == username:
                return user

        return None

    @staticmethod
    def validate(username, password):
        user = User.lookup(username)
        if user and user.password == password:
            return user

        return None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def username(self):
        return self.name


userlist = [
    User(
        id=0,
        name='admin',
        password='default',
        email='admin@pyworks.io',
        urole='admin',
        ulevel=0,
    ),
    User(
        id=1,
        name='rene',
        password='rene',
        email='rene@pyworks.io',
        urole='admin',
        ulevel=0,
    ),
    User(
        id=2,
        name='sammy',
        password='sammy',
        email='sammy@pyworks.io',
        urole='user',
        ulevel=3,
    ),
]


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.context_processor
def inject_user():
    return dict(user=current_user, error=None)


@app.route('/')
def main():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('main.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute(
        'insert into entries (title, text) values (?, ?)',
        [request.form['title'], request.form['text']],
    )
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/users', methods=['GET', 'POST'])
def users():
    return render_template('users.html', users=userlist)


@app.route('/edit_user/<user>', methods=['GET', 'POST'])
def edit_user(user):
    u = User.lookup(user)
    return render_template('edit_user.html', user=u)


@app.route('/actors', methods=['GET', 'POST'])
def actors():
    manager = app.config['PYWORKS']
    actors = []
    for module in manager.get_processes():
        actors.append(
            dict(
                name=module.name,
                mode=module.runner.state,
                qsize=module.runner.queue.qsize(),
                prio=module.prio,
                index=module.index,
                state=module.actor.pw_state().__class__.__name__,
                pid=module.pid,
            )
        )
    return render_template('actors.html', actors=actors)


@app.route('/show_actor/<name>', methods=['GET'])
def show_actor(name):
    manager = app.config['PYWORKS']
    module = manager.get_process(name)
    return render_template('show_actor.html', module=module)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.validate(username, password)
        if user:
            login_user(user)
            flash('You were logged in')
            return redirect(url_for('main'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('main'))


class RestTest(Resource):

    def get(self):
        manager = app.config['PYWORKS']
        actors = {}
        for module in manager.get_processes():
            actors[module.name] = module.actor.__class__.__name__
        return actors


api.add_resource(RestTest, '/api/actors')
