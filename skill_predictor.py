
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Literal
import joblib
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# BASE_DIR = Path(__file__).resolve().parent
# load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)
# VNV_ENV_PATH = BASE_DIR / ".vnv" / ".env"
# if VNV_ENV_PATH.exists():
#     load_dotenv(dotenv_path=VNV_ENV_PATH, override=False)

# ----------------------------
# FORCE LOAD .env FROM FILE PATH
# # ----------------------------
# BASE_DIR = Path(__file__).resolve().parent
# env_path = BASE_DIR / ".env"
# load_dotenv(dotenv_path=env_path)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# print("ADMIN USER:", ADMIN_USERNAME)
# print("ADMIN PASS:", ADMIN_PASSWORD)

# print("ADMIN USER:", os.getenv("ADMIN_USERNAME"))
# print("ADMIN PASS:", os.getenv("ADMIN_PASSWORD"))

# Utility function to hash passwords
# ----------------------------
# Password Hash Utility
# ----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


DB_NAME = "ogpredictions.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            marks INTEGER,
            accuracy INTEGER,
            time_taken INTEGER,
            attempts INTEGER,
            difficulty_level TEXT,
            topic_coverage INTEGER,
            consistency_score INTEGER,
            predicted_skill TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_students_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# Create FastAPI app
app = FastAPI(title="AI Skill Predictor API")
# sqlite database setup
create_table()
# students table setup
create_students_table()

# Admin authentication schema
class AdminAuth(BaseModel):
    username: str
    password: str

# Endpoint for admin login
@app.post("/admin/login")
def admin_login(data: AdminAuth):
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin credentials are not configured. Create a .env file with ADMIN_USERNAME and ADMIN_PASSWORD.",
        )
    if data.username == ADMIN_USERNAME and data.password == ADMIN_PASSWORD:
        return {"message": "Admin login successful"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin credentials",
    )

# Function to save prediction to database
def save_prediction(data, predicted_skill):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions (
            name,
            marks,
            accuracy,
            time_taken,
            attempts,
            difficulty_level,
            topic_coverage,
            consistency_score,
            predicted_skill,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.name,
        data.marks,
        data.accuracy,
        data.time_taken,
        data.attempts,
        data.difficulty_level,
        data.topic_coverage,
        data.consistency_score,
        predicted_skill,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

# Endpoint to get prediction history
def get_history(limit: int = 50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            marks,
            accuracy,
            time_taken,
            attempts,
            difficulty_level,
            topic_coverage,
            consistency_score,
            predicted_skill,
            created_at
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "name": row[1],
            "marks": row[2],
            "accuracy": row[3],
            "time_taken": row[4],
            "attempts": row[5],
            "difficulty_level": row[6],
            "topic_coverage": row[7],
            "consistency_score": row[8],
            "predicted_skill": row[9],
            "created_at": row[10],
        })

    return history

# Endpoint to get prediction history filtered by name
def get_history_filtered(name: str = None, limit: int = 50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if name:
        cursor.execute("""
            SELECT
                id,
                name,
                marks,
                accuracy,
                time_taken,
                attempts,
                difficulty_level,
                topic_coverage,
                consistency_score,
                predicted_skill,
                created_at
            FROM predictions
            WHERE name = ?
            ORDER BY id DESC
            LIMIT ?
        """, (name, limit))
    else:
        cursor.execute("""
            SELECT
                id,
                name,
                marks,
                accuracy,
                time_taken,
                attempts,
                difficulty_level,
                topic_coverage,
                consistency_score,
                predicted_skill,
                created_at
            FROM predictions
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "name": row[1],
            "marks": row[2],
            "accuracy": row[3],
            "time_taken": row[4],
            "attempts": row[5],
            "difficulty_level": row[6],
            "topic_coverage": row[7],
            "consistency_score": row[8],
            "predicted_skill": row[9],
            "created_at": row[10],
        })

    return history

# Endpoint to get user progress over time
def get_user_progress(name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            created_at,
            predicted_skill
        FROM predictions
        WHERE name = ?
        ORDER BY created_at ASC
    """, (name,))

    rows = cursor.fetchall()
    conn.close()

    progress = []
    for row in rows:
        progress.append({
            "date": row[0],
            "skill": row[1]
        })

    return progress


# Endpoint to get skill distribution for visualization
def get_skill_distribution():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT predicted_skill, COUNT(*) 
        FROM predictions
        GROUP BY predicted_skill
    """)

    rows = cursor.fetchall()
    conn.close()

    distribution = {}
    for skill, count in rows:
        distribution[skill] = count

    return distribution

# Load ML pipeline
model = joblib.load("skill_model.pkl")
scaler = joblib.load("scaler.pkl")
difficulty_encoder = joblib.load("difficulty_encoder.pkl")

# Student authentication schema
class StudentAuth(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)

# Input schema
class SkillInput(BaseModel):
    name: str = Field(..., min_length=1)
    marks: int = Field(..., ge=0, le=100)
    accuracy: int = Field(..., ge=0, le=100)
    time_taken: int = Field(..., gt=0)
    attempts: int = Field(..., ge=1)
    difficulty_level: Literal["easy", "medium", "hard"]
    topic_coverage: int = Field(..., ge=0, le=100)
    consistency_score: int = Field(..., ge=0, le=100)


@app.get("/")
def home():
    return {"message": "AI Skill Predictor API is running"}


@app.post("/predict")
def predict_skill(data: SkillInput):

    # Convert input to DataFrame
    input_df = pd.DataFrame([{
        "marks": data.marks,
        "accuracy": data.accuracy,
        "time_taken": data.time_taken,
        "attempts": data.attempts,
        "difficulty_level": data.difficulty_level,
        "topic_coverage": data.topic_coverage,
        "consistency_score": data.consistency_score
    }])

    # Encode difficulty level
    input_df["difficulty_level"] = difficulty_encoder.transform(
        input_df["difficulty_level"]
    )

    # Scale data
    input_scaled = scaler.transform(input_df)

    # Predict
    prediction = model.predict(input_scaled)
    predicted_skill = prediction[0]
    # Save to database
    save_prediction(data, predicted_skill)
    
    return {
         "name": data.name,
        "predicted_skill_level": predicted_skill
    }

@app.get("/history")
def fetch_history(limit: int = 50):
    return {
        "count": limit,
        "data": get_history(limit)
    }

@app.get("/analytics/skills")
def skill_analytics():
    return get_skill_distribution()

@app.get("/history/filter")
def fetch_history_filtered(name: str = None, limit: int = 50):
    return {
        "name": name,
        "count": limit,
        "data": get_history_filtered(name, limit)
    }

@app.get("/progress")
def user_progress(name: str):
    return {
        "name": name,
        "progress": get_user_progress(name)
    }

# Endpoint for student registration
@app.post("/student/register")
def register_student(data: StudentAuth):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO students (username, password_hash, created_at)
            VALUES (?, ?, ?)
        """, (
            data.username,
            hash_password(data.password),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return {"message": "Student registered successfully"}

    except sqlite3.IntegrityError:
        return {"error": "Username already exists"}

    finally:
        conn.close()

# Endpoint for student login
@app.post("/student/login")
def login_student(data: StudentAuth):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT password_hash FROM students WHERE username = ?
    """, (data.username,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": "User not found"}

    if row[0] != hash_password(data.password):
        return {"error": "Invalid password"}

    return {"message": "Login successful", "username": data.username}
