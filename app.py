from flask import Flask, render_template, render_template_string, session, redirect, url_for, request, g
from datetime import timedelta
import sqlite3
import uuid

app = Flask(__name__)

flag = app.config["FLAG"]
app.secret_key = 'secret'

app.permanent_session_lifetime = timedelta(minutes=30) 
DATABASE = './database.db'
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
)
@app.route('/', methods=['GET', 'POST'])
def get_index():
    if request.method == 'GET':
        return render_template('index.html')
    con = get_db()
    
    wish_id = uuid.uuid4()
    wish_body = request.form["wish"]
    con.execute(f"insert into angelwish(id, wish, reply) values('{wish_id}', '{wish_body}', '')")
    con.commit()
    con.close()
    return redirect(url_for('view_wish', wish_id=wish_id))

@app.route('/angel/', methods=['GET'])
def admin_page():
    if session.get("id", "") == "angel":
        return render_template('admin.html', flag=flag)
    else:
        return render_template('not_admin.html')


@app.route('/Q28/wish/<string:wish_id>/', methods=['GET'])
def view_wish(wish_id):
    con = get_db()
    data = list(con.execute(f"select wish, reply from angelwish where id='{wish_id}'"))
    con.close()
    if len(data)== 0:
        return "", 404
    wish, reply = data[0]
    return render_template('wish.html', wish=wish, reply=reply)


@app.route('/Q28/angel/<string:wish_id>/', methods=['GET'])
def view_wish_for_angel(wish_id):
    con = get_db()
    data = list(con.execute(f"select wish, reply from angelwish where id='{wish_id}'"))
    con.close()
    if len(data) == 0:
        return "", 404
    wish, reply = data[0]
    return render_template('angel_wish.html', wish=wish, reply=reply)


@app.route('/Q28/angel/<string:wish_id>/reply', methods=['POST'])
def reply(wish_id):
    con = get_db()
    reply = request.data.decode()
    con.execute(f"update angelwish set reply = '{reply}' where id = '{wish_id}'")
    con.commit()
    con.close()
    return "", 200


@app.errorhandler(500)
def internal_server_error(e):
    tmpl = 'Error: {{err}}'
    return render_template_string(tmpl, err=e.description), 500

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run()