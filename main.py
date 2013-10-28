from contextlib import closing
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import wgdb
import whitedb


# configuration
DATABASE = '/tmp/app.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()
    g.wdb = wgdb.attach_database()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select id, title, text from entries order by id desc')
    entries = [dict(eid=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    cursor = g.db.cursor()
    cursor.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    flash('New entry was successfully posted')
    g.db.commit()
    record = wgdb.create_record(g.wdb, 10)
    wgdb.set_field(g.wdb, record, 0, cursor.lastrowid)
    return redirect(url_for('show_entries'))


@app.route('/entry/<int:entry_id>')
def show_entry(entry_id):
    cur = g.db.execute('select id, title, text from entries where id=? order by id desc', (str(entry_id)))
    row = cur.fetchone()
    entry = dict(eid=row[0], title=row[1], text=row[2])
    meta = dict(views=0, upvotes=0, downvotes=0)

    try:
        query = wgdb.make_query(g.wdb, arglist=[(0, wgdb.COND_EQUAL, entry_id)])
        rec = wgdb.fetch(g.wdb, query)
    except Exception, e:
        rec = wgdb.create_record(g.wdb, 10)
        wgdb.set_field(g.wdb, rec, 0, entry_id)
    
    _, views, upvotes, downvotes = [wgdb.get_field(g.wdb, rec, col) for col in range(4)]
    views = views + 1 if views else 1
    if upvotes:
        meta['upvotes'] = upvotes
    if downvotes:
        meta['downvotes'] = downvotes
    wgdb.set_field(g.wdb, rec, 1, views)
    meta['views'] = views
    return render_template('entry.html', entry=entry, meta=meta)


@app.route('/entry/<int:entry_id>/upvote', methods=['POST'])
def entry_upvote(entry_id):
    try:
        query = wgdb.make_query(g.wdb, arglist=[(0, wgdb.COND_EQUAL, entry_id)])
        rec = wgdb.fetch(g.wdb, query)
    except Exception, e:
        rec = wgdb.create_record(g.wdb, 10)
        wgdb.set_field(g.wdb, rec, 0, entry_id)
    upvotes = wgdb.get_field(g.wdb, rec, 2)
    upvotes = upvotes + 1 if upvotes else 1
    wgdb.set_field(g.wdb, rec, 2, upvotes)
    return '{"upvotes": %d}' % upvotes

@app.route('/entry/<int:entry_id>/downvote', methods=['POST'])
def entry_downvote(entry_id):
    try:
        query = wgdb.make_query(g.wdb, arglist=[(0, wgdb.COND_EQUAL, entry_id)])
        rec = wgdb.fetch(g.wdb, query)
    except Exception, e:
        rec = wgdb.create_record(g.wdb, 10)
        wgdb.set_field(g.wdb, rec, 0, entry_id)
    downvotes = wgdb.get_field(g.wdb, rec, 3)
    downvotes = downvotes + 1 if downvotes else 1
    wgdb.set_field(g.wdb, rec, 3, downvotes)
    return '{"downvotes": %d}' % downvotes


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
