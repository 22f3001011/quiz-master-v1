from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# User Table
class User(db.Model, UserMixin):  # Inherit from UserMixin
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(255))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    quiz_attempts = db.relationship("QuizAttempt", back_populates="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Method to check password
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Subject Table
class Subject(db.Model):
    __tablename__ = "subject"  # Corrected typo
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    chapters = db.relationship("Chapter", back_populates="subject")

# Chapter Table
class Chapter(db.Model):
    __tablename__ = "chapter"  # Corrected typo
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subject = db.relationship("Subject", back_populates="chapters")
    quizzes = db.relationship("Quiz", back_populates="chapter")

# Quiz Table
class Quiz(db.Model):
    __tablename__ = "quiz"  # Corrected typo
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    quiz_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Time, nullable=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    chapter = db.relationship("Chapter", back_populates="quizzes")
    questions = db.relationship("Question", back_populates="quiz")
    quiz_attempts = db.relationship("QuizAttempt", back_populates="quiz")

# Question Table
class Question(db.Model):
    __tablename__ = "question"  # Corrected typo
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question_text = db.Column(db.Text)
    question_image_path = db.Column(db.String(255))
    option_a_text = db.Column(db.String(255))
    option_a_image_path = db.Column(db.String(255))
    option_b_text = db.Column(db.String(255))
    option_b_image_path = db.Column(db.String(255))
    option_c_text = db.Column(db.String(255))
    option_c_image_path = db.Column(db.String(255))
    option_d_text = db.Column(db.String(255))
    option_d_image_path = db.Column(db.String(255))
    correct_answer = db.Column(db.String(1), nullable=False)
    points = db.Column(db.Integer, nullable=False)

    # Relationships
    quiz = db.relationship("Quiz", back_populates="questions")
    user_answers = db.relationship("UserAnswer", back_populates="question")

# QuizAttempt Table
class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempt"  # Corrected typo
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    score = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship("User", back_populates="quiz_attempts")
    quiz = db.relationship("Quiz", back_populates="quiz_attempts")
    user_answers = db.relationship("UserAnswer", back_populates="quiz_attempt")

# UserAnswer Table
class UserAnswer(db.Model):
    __tablename__ = "user_answer"  # Corrected typo
    id = db.Column(db.Integer, primary_key=True)
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempt.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)

    # Relationships
    quiz_attempt = db.relationship("QuizAttempt", back_populates="user_answers")
    question = db.relationship("Question", back_populates="user_answers")