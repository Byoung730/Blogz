from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

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
    email = db.Column(db.String(40))
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))
    blogs = db.relationship("Blog", backref="author")
    logged_in = db.Column(db.Boolean())

    def __init__(self, username, password, email):
        self.email = email
        self.username = username
        self.password = password
        

@app.route("/", methods=['GET','POST'])
def index():

    blogs = Blog.query.all()

    return render_template('blog_template1.html', title="NerdBlog", blogs=blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['logged_in'] = True
            session['author_id'] = user.id
            flash('Welcome')
            return redirect('/')
        else:          
            flash('Error: Invalid login -- Please try again or register')
            return render_template('login.html', error=error)

    return render_template('login.html', error=error)



@app.route('/signup', methods=['POST', 'GET'])
def register():

    Password_error = None
    Username_error = None
    Email_error = None


    if request.method == 'POST':
        print(type(request.form))
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        username = request.form['username']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        print(existing_user)
        print(existing_username)
        if not existing_user and not existing_username:
            new_user = User(username, password, email)
            db.session.add(new_user)
            db.session.commit()
            print(new_user)
            # TODO - "remember" the user
            return redirect('/login')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html', Password_error=Password_error, Username_error=Username_error, Email_error=Email_error)



@app.route("/blog", methods=['GET','POST'])
def index2():

        #session['logged_in'] == False

        blogs = Blog.query.all()

        return render_template('blog_template1.html', title="NerdBlog", blogs=blogs)

@app.route("/blog_delete", methods=['GET', 'POST'])
def delete_entry():

    blog_to_delete = int(request.form['delete'])
    blogD = Blog.query.get(blog_to_delete)
    db.session.delete(blogD)
    db.session.commit()

    blogs = Blog.query.all()

    return render_template('blog_template1.html', title="NerdBlog", blogs=blogs)

@app.route("/newpost", methods=['POST', 'GET'])
def index3():

    title_error = None
    body_error = None


    blogs = Blog.query.all()

    if request.method == 'POST':

        title = request.form['blog_name']
        body = request.form['blog']
        #author = request.form['author']
        print(body)

        if title.strip(' ') == "":

            title_error = "Please enter a title"

        if body.strip(' ') == "":

            body_error = "Please type a blog"


        if not title_error and not body_error:

            blog_body = request.form['blog']
            blog_name = request.form['blog_name']

            new_blog = Blog(blog_name, blog_body, author_id=session['author_id'])
            db.session.add(new_blog)
            db.session.commit()

            newblog_id = new_blog.id
        
            blog = Blog.query.filter_by(id=newblog_id).first()

            return render_template('new_blog_template.html', title="NerdBlog", blog=blog, author=session['username'])
        
        else:

            return render_template('blog_template3.html', title="NerdBlogError", title_error=title_error, body_error=body_error)

    else:

        return render_template('blog_template3.html', title="NerdBlogNew", blogs=blogs, title_error=title_error, body_error=body_error)


@app.route("/logout", methods=['GET'])
def logout():

    #print(type(session))
    session.pop('logged_in', None)
    return redirect('/blog')


app.secret_key='LaunchCode7301981'

if __name__ == '__main__':
    app.run()