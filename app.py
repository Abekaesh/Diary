import os

import psycopg2
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

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

# Configure CS50 Library to use SQLite database
conn = psycopg2.connect(database="recipeholder", user="abe", password="123", port=5432, host="localhost")
db = conn.cursor()


@app.route("/")
@login_required
def index():
    """Show your recipe dashboard"""
    recipe_details = db.execute("""SELECT id, dish_name, updated_on FROM recipes WHERE user_id = {};""", session["user_id"])
    return render_template("index.html", recipe_details=recipe_details)

@app.route("/add_recipe", methods=["GET", "POST"])
@login_required
def add_recipe():

    if request.method == "POST":
        if not (dish_name := request.form.get("dish_name")):
            return apology("must provide name of dish")
        elif not (ingredients := request.form.get("ingredients")):
            return apology("must provide ingredients")
        elif not (recipe := request.form.get("recipe")):
            return apology("recipe not entered")
        rows = db.execute('SELECT * FROM recipes WHERE dish_name = ?;', dish_name)

        if len(rows) != 0:
            return apology(f"The dish {dish_name} already exists. Try another name.")

        db.execute("INSERT INTO recipes (user_id, dish_name, ingredients, recipe) VALUES (%s, %s, %s, %s);",
                    session["user_id"], dish_name, ingredients, recipe)

        flash("Recipe added successfully !!")

        return redirect("/")
    else:
        return render_template("add_recipe.html")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        if not (dish_name := request.form.get("dish_name")):
            return apology("MISSING DISH NAME")
        if not (query := db.execute("SELECT * FROM recipes WHERE dish_name = %s;", dish_name)):
            return apology("INVALID DISH NAME")
        Id = query[0]["id"]
        db.execute("DELETE FROM recipes WHERE dish_name = %s;", dish_name)
        db.execute("UPDATE recipes SET id = id-1 WHERE id > %s;", Id)

        flash("Recipe deleted successfully !!")
        return redirect("/")
    else:
        return render_template("delete.html")


@app.route("/recipe", methods = ["GET", "POST"])
@login_required
def recipe():
    if request.method == "POST":
        if not (dish_name := request.form.get("dish_name")):
            return apology("MISSING DISH NAME")
        if not (query := db.execute("SELECT * FROM recipes WHERE dish_name = %s AND user_id = %s;", dish_name, session["user_id"])):
            return apology("INVALID DISH NAME")
        flash("Recipe displayed below !!")
        return render_template("recipe.html", dish_name=dish_name, ingredients=query[0]["ingredients"], recipe=query[0]["recipe"])
    else:
        return render_template("recipe.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = %s", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")





@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not (username := request.form.get("username")):
            return apology("MISSING USERNAME")

        if not (password := request.form.get("password")):
            return apology("MISSING PASSWORD")

        if not (confirmation := request.form.get("confirmation")):
            return apology("MISSING CONFIRMATION")

        rows = db.execute(f"SELECT * FROM users WHERE username = {username};")

        if len(rows) != 0:
            return apology(f"The username {username} already exists. Try another username.")

        if password != confirmation:
            return apology("Password not Matched")

        Id = db.execute(f"INSERT INTO users (username,hash) VALUES ({username},{generate_password_hash(password)});" )

        session["user_id"] = Id

        flash("Registered Successfully!!")

        return redirect("/")

    else:

        return render_template("register.html")


@app.route("/reset", methods=["GET", "POST"])
@login_required
def reset():
    if request.method == "POST":
        if not (password := request.form.get("password")):
            return apology("MISSING OLD PASSWORD")

        rows = db.execute("SELECT * FROM users WHERE id = %s;", session["user_id"])

        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("INVALID PASSWORD")

        if not (new_password := request.form.get("new_password")):
            return apology("MISSING NEW PASSWORD")

        if not (confirmation := request.form.get("confirmation")):
            return apology("MISSING CONFIRMATION")

        if new_password != confirmation:
            return apology("PASSWORD NOT MATCH")

        db.execute("UPDATE users set hash = %s WHERE id = %s;",
                   generate_password_hash(new_password), session["user_id"])

        flash("Password reset successful!")

        return redirect("/")
    else:
        return render_template("reset_password.html")





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
