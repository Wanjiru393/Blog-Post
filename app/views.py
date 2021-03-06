from flask import  render_template, url_for, flash,redirect,request,abort, json
from app import app, db, bcrypt,mail
from .forms import RegistrationForm, LoginForm,StringField, PostForm,RequestResetForm, ResetPasswordForm
from .models import User,Post
from flask_login import login_user,current_user, logout_user, login_required
import requests
import smtplib
from flask_mail import  Message





@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page',1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()) .paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts)


@app.route('/quote', methods=['GET','POST'])
def quote():
    req = requests.get('http://quotes.stormconsultancy.co.uk/random.json')
    data = json.loads(req.content)
    return render_template('quote.html', data=data)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password  = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created successfully! ', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
      if current_user.is_authenticated:
            return redirect(url_for('home'))
      form = LoginForm()
      if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
      return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

#POSTS

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Blog Post has been created !', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Blog',
                           form=form, legend='New Blog')


@app.route("/post/<int:post_id>")
def post(post_id):
    print(post_id)
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)



@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your Blog has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Blog',
                           form=form, legend='Update Blog')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))



# @app.route('/comments/<int:post_id>', methods=['POST', 'GET'])
# @login_required
# def comment():
#     post = Post.query.get_or_404(post_id)
#     form = CommentForm()
#     allComments = Comment.query.filter_by(post_id=post_id).all()
#     if form.validate_on_submit():
#         postedComment = Comment(comment=form.comment.data,
#                                 user_id=current_user.id, post_id=post_id)
#         post_id = post_id
#         db.session.add(postedComment)
#         db.session.commit()
#         flash('Comment added successfully')

#         return redirect(url_for('comment', post_id=post_id))

#     return render_template("comment.html", post=post, title='React to Blog!', form=form, allComments=allComments)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request', sender='noreply@gmail.com', 
    recipients=[user.email])

    msg.body = f''' To reset password,visit the link below
{url_for('reset_token',token=token, _external = True)}

If you did not initiate this request,kindly ignore this.
'''



@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated():
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('A Password reset email has been sent to your address','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title ='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated():
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password  = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Password Reset successfully! ', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_token.html', title ='Reset Password', form=form)