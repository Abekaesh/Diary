from flask import *
from flask_session import Session
from tempfile import mkdtemp
from helpers import login_required
import psycopg2

app = Flask(__name__)
id = 0
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request 
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database connection
conn = psycopg2.connect(database="diary", user="admin", password="admin", port=5432, host="localhost")
db = conn.cursor()
conn.rollback()
conn.set_session(autocommit=True)

app.secret_key='diary'
@app.route("/")
def home():
    return render_template(
        "index.html"
    )

@app.route("/vision")
def vision():
    return render_template(
        "about.html"
    )

@app.route("/dashboard",  methods=["GET", "POST"])
@login_required
def dashboard():

    db.execute("SELECT * FROM tags;")
    tags_present = db.fetchall()
    if request.method == "POST":
        if (date_entry := request.form.get('d_entry')):
            tag = request.form.get('taglist')
            if tag == 'all':
                db.execute("SELECT * FROM diary_entry WHERE user_id = '{}' AND created_at = '{}' ORDER BY created_at DESC;".format(session['user_id'], date_entry))
                entries = db.fetchall()
                print(entries,1)
                return render_template('dashboard.html', entries=entries, tags_present=tags_present)
            else:
                db.execute("SELECT * FROM diary_entry JOIN entry_tag ON diary_entry.entry_id = entry_tag.entry_id WHERE user_id = '{}' AND created_at = '{}' AND tag_id IN (SELECT tag_id FROM tags WHERE tag_name = '{}') ORDER BY created_at DESC;".format(session['user_id'], date_entry, tag))
                entries = db.fetchall()
                print(entries,2)
                return render_template('dashboard.html', entries=entries, tags_present=tags_present)
        else:
            tag = request.form.get('taglist')
            print(tag)
            if tag!= None and tag!='all':
                db.execute("SELECT * FROM diary_entry JOIN entry_tag ON diary_entry.entry_id = entry_tag.entry_id WHERE user_id = '{}' AND tag_id IN (SELECT tag_id FROM tags WHERE tag_name = '{}') ORDER BY created_at DESC;".format(session['user_id'], tag))
                entries = db.fetchall()
                print(entries,3)
                return render_template('dashboard.html', entries=entries, tags_present=tags_present)
            else:
                db.execute("SELECT * FROM diary_entry WHERE user_id = '{}' ORDER BY created_at DESC;".format(session['user_id']))
                entries = db.fetchall()
                print(entries,4)
                return render_template('dashboard.html', entries=entries, tags_present=tags_present)
    
    db.execute("SELECT * FROM diary_entry WHERE user_id = '{}' ORDER BY created_at DESC;".format(session['user_id']))
    entries = db.fetchall()
    return render_template(
        "dashboard.html", entries=entries, tags_present=tags_present
    )

@app.route("/write", methods=["GET", "POST"])
@login_required
def write():
    if request.method == "POST":
        db.execute("SELECT * FROM diary_entry;")
        r2 = db.fetchall()
        entryid = len(r2) + 1
        tags = request.form.get('tagname')
        experience = request.form.get('experience')
        tagnames = tags.split(',')
        db.execute("INSERT INTO diary_entry(entry_id, user_id, entry_text) VALUES ('{}','{}','{}');".format(entryid, session['user_id'], experience))

        for tag in tagnames:
            db.execute("SELECT * FROM tags;")
            r1 = db.fetchall()
            
            db.execute("SELECT * FROM tags WHERE tag_name = '{}';".format(tag))
            rows = db.fetchone()
            if rows is None:
                tagid = len(r1) + 1
                db.execute("INSERT INTO tags(tag_id, tag_name) VALUES('{}', '{}');".format(tagid, tag))
                db.execute("INSERT INTO entry_tag(entry_id, tag_id) VALUES ('{}','{}');".format(entryid, tagid))
            else:
                db.execute("SELECT tag_id FROM tags WHERE tag_name = '{}';".format(tag))
                r3 = db.fetchall()
                tagid = r3[0][0]
                db.execute("INSERT INTO entry_tag(entry_id, tag_id) VALUES ('{}','{}');".format(entryid, tagid))


        flash("Your feelings are safe with me")
        return redirect(url_for('dashboard'))
    return render_template(
        "write.html"
    )

@app.route("/signin", methods=["GET","POST"])
def signin():
    global id
    if request.method=="POST":
        name = request.form.get('username')
        mailid = request.form.get('mailid')
        dob = request.form.get('dob')
        password = request.form.get('pass')
        check_password = request.form.get('repass')
        query = "SELECT * FROM users WHERE email = '{}';".format(mailid)
        db.execute(query)
        rows = db.fetchall()
        if len(rows) != 0:
            flash(f"The email {mailid} already exists. Try another email.")
            redirect(url_for('signin'))
        elif password != check_password:
            flash("Password not matching!")
            redirect(url_for('signin'))
        else:
            db.execute("SELECT * FROM users;")
            ids = db.fetchall()
            id = len(ids) + 1
            db.execute("INSERT INTO users (user_id, name, email, password, dob) VALUES ('{}', '{}', '{}', '{}', '{}');".format(id,name,mailid,password,dob) )
            
            session['user_id'] = id
            flash("You are registered")
            return redirect(url_for('dashboard'))
    return render_template(
        "signin.html"
    )

@app.route("/login", methods=["GET","POST"])
def login():
    global id
    session.clear()
    if request.method=="POST":
        mailid = request.form.get('mailid')
        password = request.form.get('pass')
        query = "SELECT * FROM users WHERE email = '{}' AND password = '{}';".format(mailid, password)
        db.execute(query)
        rows = db.fetchall()
        print(rows)
        if len(rows) == 0:
            flash("Wrong username or password!")
            redirect(url_for('login'))
        else:
            session['user_id'] = rows[0][0]
            flash("Welcome to your diary!")
            return redirect(url_for('dashboard'))
    return render_template(
        "login.html"
    )

@app.route('/logout')
def logout():
    session.clear()
    flash("See you later :)")
    return redirect(url_for('home'))