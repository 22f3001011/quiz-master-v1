from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from functools import wraps
from datetime import datetime
from extensions import db
from models import User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer

app = Flask(__name__)

# Correct configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for Flask-Login

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

    admin_email = "22f3001011@ds.study.iitm.ac.in"
    admin_password = "Admin123"

    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            email=admin_email,
            full_name="Admin",
            qualification="Admin",
            dob=datetime.strptime("2003-10-18", "%Y-%m-%d").date(),
            is_admin=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return "Welcome to the Quiz App"

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(email=email, full_name=full_name, qualification=qualification, dob=dob)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)  # Log in the user
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# User Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Admin Dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html')

# User Dashboard
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html')


# Ensure admin access
def admin_required(func):
    @wraps(func)  # Preserve function metadata
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_required(func)(*args, **kwargs)  # Redirect to login if not logged in

        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('index'))

        return func(*args, **kwargs)
    return wrapper
# CRUD for Subjects


@app.route('/admin/subjects', methods=['GET', 'POST'])
@admin_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@app.route('/admin/subjects/delete/<int:subject_id>', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted!', 'success')
    return redirect(url_for('manage_subjects'))

# CRUD for Chapters
@app.route('/admin/chapters/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def manage_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        chapter = Chapter(name=name, description=description, subject_id=subject.id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added!', 'success')
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    return render_template('admin/chapters.html', subject=subject, chapters=chapters)

@app.route('/admin/chapters/delete/<int:chapter_id>', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted!', 'success')
    return redirect(url_for('manage_chapters', subject_id=chapter.subject_id))

# CRUD for Quizzes
@app.route('/admin/quizzes/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def manage_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        quiz_date = datetime.strptime(request.form['quiz_date'], "%Y-%m-%d")
        duration = request.form['duration']
        remarks = request.form.get('remarks', '')
        quiz = Quiz(chapter_id=chapter.id, quiz_date=quiz_date, duration=duration, remarks=remarks)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added!', 'success')
    quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
    return render_template('admin/quizzes.html', chapter=chapter, quizzes=quizzes)

@app.route('/admin/quizzes/delete/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted!', 'success')
    return redirect(url_for('manage_quizzes', chapter_id=quiz.chapter_id))

# CRUD for Questions
@app.route('/admin/questions/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def manage_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        question_text = request.form['question_text']
        correct_answer = request.form['correct_answer']
        points = int(request.form['points'])

        question = Question(
            quiz_id=quiz.id,
            question_text=question_text,
            correct_answer=correct_answer,
            points=points
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added!', 'success')
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    return render_template('admin/questions.html', quiz=quiz, questions=questions)

@app.route('/admin/questions/delete/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted!', 'success')
    return redirect(url_for('manage_questions', quiz_id=question.quiz_id))

# View all users
@app.route('/admin/users')
@admin_required
def view_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


if __name__ == "__main__":
    app.run(debug=True)
