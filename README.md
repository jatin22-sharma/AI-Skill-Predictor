AI Skill Predictor Tool
Overview
The AI Skill Predictor Tool is a full-stack learning analytics application that predicts a student's skill level based on test performance and behavior.

The system classifies students into Beginner, Intermediate, or Advanced using a machine learning model trained on multiple performance factors.

Features
Student
Secure login and registration
AI-based skill prediction
Personal prediction history
Skill progress visualization
Admin
Role-based admin access
Analytics dashboard
Skill distribution analysis
Leaderboard of top-performing students
Student-specific performance insights
CSV export for reporting
Tech Stack
Frontend: Streamlit
Backend: FastAPI
Database: SQLite
Machine Learning: Scikit-learn
Data Analysis: Pandas, Plotly
How to Clone the Repository
git clone https://github.com/Mohnish4246/AI-Skill-Predictor.git
How to Run Locally
Note :
python 3.11 version is required to install the requirements.txt
To see the Data in the DataBase you have to install DB Browser(SQLite) from any browser.
Create Virtual Environment
python3.11 -m venv .venv
Activate Virtual Environment
on Windows
.venv\Scripts\activate
on macOS / Linux
source .venv/bin/activate
1. Install dependencies
pip install -r requirements.txt
Note
You also have to create a .env file for ADMIN_USERNAME and ADMIN_PASSWORD
Then add your username and password in it so that it can access that while you login as admin
2. Start backend
python -m uvicorn main:app --reload
3. Start frontend
streamlit run app.py
Deactivate Virtual Environment
deactivate
Project Goal
To demonstrate how machine learning, data analytics, and full-stack development can be combined to build a secure and scalable skill evaluation system.


