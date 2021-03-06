from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#Define classes:

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    body = db.Column(db.String(5000))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    def __init__(self, name, body, author_id):
        self.name = name
        self.body = body
        self.author_id = author_id

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))
    blogs = db.relationship("Blog", backref="author")
    logged_in = db.Column(db.Boolean())

    def __init__(self, username, password, email):
        self.email = email
        self.username = username
        self.password = password


#Routes and functions:

@app.route("/", methods=['GET','POST'])
def index():

    blogs = Blog.query.all()

    return render_template('blog_template1.html', title="NerdBlog", blogs=blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    #Login Verification

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        #Code testing
        #print(password)
        #print(username)
        #print(user)
        #print(user.password)

        if user and user.password == password:
            session['logged_in'] = True
            session['author_id'] = user.id
            flash('Welcome')
            return redirect('/')
        else:          
            flash('Error: Invalid login -- Please try again or register')
            return redirect('/login')

    return render_template('login.html', error=error)



@app.route('/signup', methods=['POST', 'GET'])
def register():

    Password_error = None
    Username_error = None
    Email_error = None


    if request.method == 'POST':

        #print(type(request.form)) -- Checking code in command prompt
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        username = request.form['username']

        #Validate user's data:

        if len(username) < 2 or len(username) > 30:

            flash('Invalid Username -- too short or too long')
            return redirect("/signup")

        if password != verify:

            flash("Passwords do not match")
            return redirect("/signup")

        if '@' not in email:

            flash("Invalid Email address")
            return redirect("/signup")


        else:
            existing_user = User.query.filter_by(email=email).first()
            existing_username = User.query.filter_by(username=username).first()
            print(existing_user)
            print(existing_username)
            if not existing_user and not existing_username:
                new_user = User(username, password, email)
                db.session.add(new_user)
                db.session.commit()
                #print(new_user) -- I was checking my code in the command prompt
                return redirect('/login')
            else:
                return "<h1>Duplicate user</h1>"

    return render_template('signup.html', Password_error=Password_error, Username_error=Username_error, Email_error=Email_error)



@app.route("/blog", methods=['GET','POST'])
def index2():

        #session['logged_in'] == False -- I don't think I need this

        blogs = Blog.query.all()

        return render_template('blog_template1.html', title="NerdBlog", blogs=blogs)

@app.route("/blog_delete", methods=['GET', 'POST'])
def delete_entry():

    #code check:
    #print(session['author_id'])
    #print(request.form['author_id'])

    #Delete individual blogs -- Only the author can delete their own blogs

    if session['author_id'] == int(request.form['author_id']):
        blog_to_delete = int(request.form['delete'])
        blogD = Blog.query.get(blog_to_delete)
        db.session.delete(blogD)
        db.session.commit()

        blogs = Blog.query.all()

        return render_template('blog_template1.html', title="NerdBlog", blogs=blogs)

    blogs = Blog.query.all()

    flash('Not your entry -- Cannot delete')
    return render_template('blog_template1.html', title="NerdBlog", blogs=blogs)


@app.route("/newpost", methods=['POST', 'GET'])
def index3():

    title_error = None
    body_error = None


    blogs = Blog.query.all()

    if request.method == 'POST':

        title = request.form['blog_name']
        body = request.form['blog']
        #author_id = request.form['author_id'] -- I don't think I need this
        #print(body) -- checking my code in command prompt


        #Preventing empty entries:
        if title.strip(' ') == "":

            title_error = "Please enter a title"

        if body.strip(' ') == "":

            body_error = "Please type a blog"


        if not title_error and not body_error:
            #If all is well, update database

            blog_body = request.form['blog']
            blog_name = request.form['blog_name']
            new_blog = Blog(blog_name, blog_body, author_id=session['author_id'])
            db.session.add(new_blog)
            db.session.commit()

            newblog_id = new_blog.id
        
            blog = Blog.query.filter_by(id=newblog_id).first()

            return render_template('new_blog_template.html', title="NerdBlog", blog=blog, author_id=session['author_id'])
        
        else:
            #error stuff
            return render_template('blog_template3.html', title="NerdBlogError", title_error=title_error, body_error=body_error)

    else:
        #I forgot why I put this in here
        return render_template('blog_template3.html', title="NerdBlogNew", blogs=blogs, title_error=title_error, body_error=body_error)


@app.route("/logout", methods=['GET'])
def logout():

    #print(type(session)) -- checking code in command prompt
    session.pop('logged_in', None)
    return redirect('/blog')


app.secret_key='LaunchCode7301981'

if __name__ == '__main__':
    app.run()