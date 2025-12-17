import os
import re
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import markdown

app = Flask(__name__)

@app.template_filter('markdown')
def render_markdown(text):
    return markdown.markdown(text)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context Processor to inject posts into all templates (for sidebar)
@app.context_processor
def inject_posts():
    return {'db_posts': Post.query.all()}

# Routes
@app.route('/')
def index():
    page = Page.query.filter_by(slug='index').first_or_404()
    return render_template('index.html', page=page)

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/post/<slug>')
def show_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('post_detail.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        
        # Basic validation
        if not title or not content:
            flash('Title and Content are required!', 'danger')
        else:
            if not slug:
                slug = title.lower().replace(' ', '-')
            
            new_post = Post(title=title, slug=slug, content=content)
            db.session.add(new_post)
            try:
                db.session.commit()
                flash('Post created successfully!', 'success')
                return redirect(url_for('show_post', slug=slug))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating post: {str(e)}', 'danger')

    return render_template('create_post.html')

@app.route('/post/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title')
        slug_new = request.form.get('slug')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Title and Content are required!', 'danger')
        else:
            if not slug_new:
                slug_new = title.lower().replace(' ', '-')
                
            post.title = title
            post.slug = slug_new
            post.content = content
            
            try:
                db.session.commit()
                flash('Post updated successfully!', 'success')
                return redirect(url_for('show_post', slug=post.slug))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating post: {str(e)}', 'danger')

    return render_template('edit_post.html', post=post)



@app.route('/post/<slug>/delete', methods=['POST'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post has been deleted!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting post: {str(e)}', 'danger')
        return redirect(url_for('show_post', slug=post.slug))

@app.route('/page/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Title and Content are required!', 'danger')
        else:
            page.title = title
            page.content = content
            
            try:
                db.session.commit()
                flash('Page updated successfully!', 'success')
                if slug == 'index':
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for(slug))  # For about, etc.
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating page: {str(e)}', 'danger')

    return render_template('edit_page.html', page=page)

# Initialize DB and Admin
def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('TALHA@123mahamud') # Default password
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin / admin123")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
