from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date ,datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea 
#from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = "@Younes1337"

#add database 
 
#mySql DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/our_users'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)

    author = db.Column(db.String(255))
    dates_posted = db.Column(db.DateTime, default=datetime.utcnow())
    slug = db.Column(db.String(255))

#Creating a Post Form
class PostForm(FlaskForm):
    title = StringField("Title", validators = [DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget = TextArea())
    author = StringField("Author", validators=[DataRequired()]) 
    slug = StringField("Slug", validators = [DataRequired()])
    submit =  SubmitField("Submit") 

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post) 

@app.route('/post/edit/<int:id>', methods=['POST', 'GET'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
       post.title = form.title.data
       post.author = form.author.data 
       post.slug = form.slug.data
       post.content = form.content.data  
       #Update your database :
       db.session.add(post)
       db.session.commit()
       flash('Post has been updated')
       return redirect(url_for('post', id=post.id))

    form.title.data = post.title
    form.author.data = post.author 
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)     

@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.dates_posted)

    
    return render_template('posts.html', posts=posts)



#Add a Post Page :
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title = form.title.data, content = form.content.data, author = form.author.data, slug = form.slug .data)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()

        flash('Blog Post Submitted Successfully!')
    #Redirect to the webPage 
    return render_template('add_post.html', form=form)

#Creating a Request :
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request = db.Column(db.String(255))
    service = db.Column(db.String(255))
    your_opinion = db.Column(db.String(255))
    resuest_date = db.Column(db.DateTime, default=datetime.utcnow)

class RequestForm(FlaskForm):
          request = StringField("Your request:", validators=[DataRequired()])
          service = StringField("Service:", validators=[DataRequired()]) 
          your_opinion = StringField("Your opinion:", validators=[DataRequired()], widget=TextArea())
          submit = SubmitField('Submit')

#Creating Request web Page 
@app.route('/req-ser', methods=['GET', 'POST'])
def add_request():
    form = RequestForm()
    if form.validate_on_submit():
       req = Request(request=form.request.data, service=form.service.data, your_opinion=form.your_opinion.data)
       form.request.data = '' 
       form.service.data = ''
       form.your_opinion.data = ''

       db.session.add(req)
       db.session.commit()

       flash('Your request has been Submitted Succefully')
    #redirecting to ou webPage 
    return render_template('add_request.html', form=form)

 

@app.route('/date')
def get_current_date():
    favorite_pizza = {
            "Jhon": "Pepeorni",
            "Younes": "Tagla",
            "Tim": "Mushroom"
    }
    return favorite_pizza
    #return {'Date': datetime.utcnow()}


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable = False ,unique = True)
    favorite_color= db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not matched')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)     

    def __repr__(self):
        return '<Name %r>' % self.name


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None 
    form = UserForm()

    try :
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Succefully!!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('user_add.html', form = form, name = name, our_users = our_users)
    except :
        flash("Ooops!! There was a problem!!")
        return render_template('user_add.html', form = form, name = name, our_users = our_users)


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min = 5, max = 15)])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("favorite color")
    password_hash = PasswordField('Password', validators = [DataRequired(), Length(min = 5), EqualTo('password_hash2', message = 'Passwords must matches !!')])
    password_hash2 = PasswordField('Confirm Password', validators = [DataRequired()])
    submit = SubmitField("submit")


class NamerForm(FlaskForm):
    name = StringField("What's Your name", validators=[DataRequired(), Length(min = 5, max = 15)])
    submit = SubmitField("submit")
#password Form :
class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired(), Length(min = 5, max = 15)])
    password_hash = PasswordField("Enter Your Password", validators=[DataRequired()])
    submit = SubmitField("submit")




@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name'] 
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try :
            db.session.commit()
            flash("User updated Successfully!")
            return render_template('update.html', name_to_update = name_to_update,
                                  form = form)
        except : 
            flash("OOOPS!!! Looks like There was a problem, try again ....")
            return render_template('update.html', name_to_update = name_to_update,
                                  form = form)
    else :
        return render_template('update.html', name_to_update = name_to_update,
                                  form = form, id=id)    


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('505.html'), 500 

@app.route('/name', methods=["GET", "POST"])
def name():
    name = None 
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Succefully!!")
    return render_template('index.html', name = name ,form= form)


@app.route('/user/add', methods=["GET", "POST"])
def add_user():
    name = None 
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None :
            hashed_password = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name = form.name.data, email = form.email.data, favorite_color = form.favorite_color.data, password_hash = hashed_password)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = '' 
        form.favorite_color.data = '' 
        form.password_hash.data = ''
        flash('User Added Successfully')
    our_users = Users.query.order_by(Users.date_added)      
    return render_template('user_add.html', form = form, name = name, our_users = our_users)

#Password Test Page :
@app.route('/test_pw', methods=["GET", "POST"])
def test_pw():
    email = None
    password = None 
    pw_to_check = None 
    passed = None  
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        #clear the form 

        form.email.data = ''
        form.password_hash.data = ''
        pw_to_check = Users.query.filter_by(email=email).first()    

    return render_template('test_py.html', 
        email = email,   
        password = password, 
        pw_to_check = pw_to_check, 
        form= form)    






