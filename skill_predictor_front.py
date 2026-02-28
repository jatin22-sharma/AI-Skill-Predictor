
import streamlit as st
import requests
import pandas as pd

# ==================================
# PAGE CONFIG (MUST BE FIRST)
# ==================================
st.set_page_config(
    page_title="AI Skill Predictor",
    page_icon="🧠",
    layout="centered"
)

BACKEND_URL = "http://127.0.0.1:8001"

# ==================================
# SESSION STATE INIT
# ==================================
if "student_logged_in" not in st.session_state:
    st.session_state.student_logged_in = False
    st.session_state.student_name = None

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ==================================
# AUTH GUARDS
# ==================================
def require_student_login():
    if not st.session_state.student_logged_in:
        st.warning("⚠️ Student login required.")
        st.stop()

def require_admin_login():
    if not st.session_state.admin_logged_in:
        st.warning("⚠️ Admin login required.")
        st.stop()

# ==================================
# ROLE-BASED SIDEBAR
# ==================================
st.sidebar.title("Navigation")

# CASE 1: No one is logged in (PUBLIC)
if not st.session_state.student_logged_in and not st.session_state.admin_logged_in:
    menu = st.sidebar.radio(
        "Menu",
        ["Project Overview", "Student Login", "Admin Login"]
    )

# CASE 2: Student logged in
elif st.session_state.student_logged_in:
    menu = st.sidebar.radio(
        "Student Menu",
        ["Skill Prediction", "My History", "My Progress"]
    )

# CASE 3: Admin logged in
elif st.session_state.admin_logged_in:
    menu = st.sidebar.radio(
        "Admin Menu",
        ["Admin Overview", "Student Analytics"]
    )

# ==================================
# STUDENT LOGIN
# ==================================
# ==================================
# PROJECT OVERVIEW (PUBLIC HOME PAGE)
# ==================================
if menu == "Project Overview":

    st.title("AI Skill Predictor Tool")

    st.subheader("Project Overview")

    st.write(
        """
        The AI Skill Predictor Tool is a learning analytics application designed
        to evaluate and track a student's skill level based on test performance
        and behavioral patterns.
        """
    )

    st.write(
        """
        This system uses machine learning to analyze multiple performance factors
        and predicts a skill level as Beginner, Intermediate, or Advanced.
        """
    )

    st.divider()

    st.subheader("What this project does")

    st.markdown(
        """
        - Allows students to register and log in securely
        - Predicts a student's skill level using an AI model
        - Stores predictions in a database for future analysis
        - Shows students their personal history and progress
        - Provides administrators with a complete analytics dashboard
        """
    )

    st.divider()

    st.subheader("How the prediction works")

    st.markdown(
        """
        The system evaluates multiple performance indicators, including:
        - Accuracy of answers
        - Difficulty level of the test
        - Consistency in performance
        - Number of attempts required
        - Time taken to complete the test
        """
    )

    st.write(
        """
        Based on these inputs, the machine learning model identifies patterns
        and predicts the most suitable skill level.
        """
    )

    st.divider()

    st.subheader("Student features")

    st.markdown(
        """
        - Predict skill level
        - View personal prediction history
        - Track skill progress over time
        - Access only personal data
        """
    )

    st.divider()

    st.subheader("Admin features")

    st.markdown(
        """
        - View all student predictions
        - Analyze overall skill distribution
        - Identify top-performing students
        - Analyze individual student performance
        - Export prediction data for reporting
        """
    )

    st.divider()

    st.subheader("Technologies used")

    st.markdown(
        """
        - Frontend: Streamlit  
        - Backend: FastAPI  
        - Database: SQLite  
        - Machine Learning: Scikit-learn  
        - Data Analysis and Visualization: Pandas, Plotly  
        """
    )

    st.divider()

    st.subheader("Project goal")

    st.write(
        """
        The goal of this project is to demonstrate how artificial intelligence,
        data analytics, and full-stack development can be combined to build
        a practical, secure, and scalable learning evaluation system.
        """
    )

    st.info("Use the sidebar to log in as a student or admin to continue.")


elif menu == "Student Login":
    st.title("👤 Student Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            try:
                r = requests.post(
                    f"{BACKEND_URL}/student/login",
                    json={"username": username, "password": password},
                    timeout=10,
                )
                res = r.json()
            except requests.RequestException as e:
                st.error(f"Backend connection error: {e}")
            except ValueError:
                st.error(f"Backend returned invalid JSON (status {r.status_code}).")
            else:
                if r.ok and "message" in res:
                    st.session_state.student_logged_in = True
                    st.session_state.student_name = res["username"]
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error(res.get("detail") or res.get("error") or "Login failed.")

    with col2:
        if st.button("Register"):
            try:
                r = requests.post(
                    f"{BACKEND_URL}/student/register",
                    json={"username": username, "password": password},
                    timeout=10,
                )
                res = r.json()
            except requests.RequestException as e:
                st.error(f"Backend connection error: {e}")
            except ValueError:
                st.error(f"Backend returned invalid JSON (status {r.status_code}).")
            else:
                if r.ok and "message" in res:
                    st.success("Registered successfully. Please login.")
                else:
                    st.error(res.get("detail") or res.get("error") or "Registration failed.")

# ==================================
# ADMIN LOGIN
# ==================================
elif menu == "Admin Login":
    st.title("🔐 Admin Login")

    u = st.text_input("Admin Username")
    p = st.text_input("Admin Password", type="password")

    if st.button("Login as Admin"):
        try:
            r = requests.post(
                f"{BACKEND_URL}/admin/login",
                json={"username": u, "password": p},
                timeout=10,
            )
            res = r.json()
        except requests.RequestException as e:
            st.error(f"Backend connection error: {e}")
        except ValueError:
            st.error(f"Backend returned invalid JSON (status {r.status_code}).")
        else:
            if r.ok and "message" in res:
                st.session_state.admin_logged_in = True
                st.success("Admin login successful")
                st.rerun()
            else:
                st.error(res.get("detail") or res.get("error") or "Admin login failed.")

# ==================================
# SKILL PREDICTION (STUDENT)
# ==================================
elif menu == "Skill Prediction":
    require_student_login()

    st.title("🧠 Skill Prediction")
    st.caption(f"Logged in as **{st.session_state.student_name}**")

    with st.form("predict_form"):
        marks = st.number_input("Marks", 0, 100, 70)
        accuracy = st.number_input("Accuracy (%)", 0, 100, 75)
        time_taken = st.number_input("Time Taken (minutes)", 1, 120, 30)
        attempts = st.number_input("Attempts", 1, 10, 2)
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
        topic = st.number_input("Topic Coverage (%)", 0, 100, 80)
        consistency = st.number_input("Consistency Score (%)", 0, 100, 75)

        submit = st.form_submit_button("Predict")

    if submit:
        payload = {
            "name": st.session_state.student_name,
            "marks": marks,
            "accuracy": accuracy,
            "time_taken": time_taken,
            "attempts": attempts,
            "difficulty_level": difficulty,
            "topic_coverage": topic,
            "consistency_score": consistency
        }

        res = requests.post(
            f"{BACKEND_URL}/predict",
            json=payload
        ).json()

        st.success(f"Predicted Skill Level: **{res['predicted_skill_level']}**")

# ==================================
# MY HISTORY (STUDENT)
# ==================================
elif menu == "My History":
    require_student_login()

    st.title("📜 My History")

    res = requests.get(
        f"{BACKEND_URL}/history/filter",
        params={"name": st.session_state.student_name}
    ).json()

    df = pd.DataFrame(res["data"])
    st.dataframe(df, use_container_width=True)

# ==================================
# MY PROGRESS (STUDENT)
# ==================================
elif menu == "My Progress":
    require_student_login()

    st.title("📈 My Progress")

    res = requests.get(
        f"{BACKEND_URL}/progress",
        params={"name": st.session_state.student_name}
    ).json()

    df = pd.DataFrame(res["progress"])

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["skill_value"] = df["skill"].map({
            "Beginner": 1,
            "Intermediate": 2,
            "Advanced": 3
        })
        st.line_chart(df.set_index("date")["skill_value"])

# ==================================
# ADMIN OVERVIEW DASHBOARD
# ==================================
elif menu == "Admin Overview":
    require_admin_login()

    st.title("🛠 Admin Overview Dashboard")

    res = requests.get(f"{BACKEND_URL}/history").json()
    df = pd.DataFrame(res["data"])

    if df.empty:
        st.info("No data available.")
    else:
        # ---------------- KPIs ----------------
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Predictions", len(df))
        col2.metric("Total Students", df["name"].nunique())
        col3.metric("Avg Consistency", round(df["consistency_score"].mean(), 2))

        st.divider()

        # ---------------- SKILL DISTRIBUTION ----------------
        st.subheader("🎯 Skill Distribution (Overall)")

        skill_counts = df["predicted_skill"].value_counts()

        donut_df = pd.DataFrame({
            "Skill": skill_counts.index,
            "Count": skill_counts.values
        })

        st.plotly_chart(
            {
                "data": [{
                    "labels": donut_df["Skill"],
                    "values": donut_df["Count"],
                    "type": "pie",
                    "hole": 0.4
                }],
                "layout": {
                    "title": "Skill Level Proportion"
                }
            },
            use_container_width=True
        )

        # ---------------- DIFFICULTY VS SKILL ----------------
        st.subheader("📘 Difficulty vs Skill Outcome")

        pivot = pd.crosstab(
            df["difficulty_level"],
            df["predicted_skill"]
        )

        st.dataframe(pivot, use_container_width=True)
        st.bar_chart(pivot)

        # ---------------- CONSISTENCY VS SKILL ----------------
        st.subheader("📊 Consistency Score Distribution by Skill")

        st.plotly_chart(
            {
                "data": [
                    {
                        "y": df[df["predicted_skill"] == skill]["consistency_score"],
                        "type": "box",
                        "name": skill
                    }
                    for skill in df["predicted_skill"].unique()
                ],
                "layout": {
                    "title": "Consistency Score vs Skill Level",
                    "yaxis": {"title": "Consistency Score"}
                }
            },
            use_container_width=True
        )


        # ---------------- LEADERBOARD ----------------
        st.subheader("🏆 Leaderboard (Top Consistent Students)")
        leaderboard = (
            df.groupby("name")["consistency_score"]
            .mean()
            .sort_values(ascending=False)
            .head(5)
        )
        st.dataframe(leaderboard.reset_index(name="Avg Consistency Score"))

        # ---------------- MONTHLY TREND ----------------
        st.subheader("📅 Monthly Skill Improvement Trend")
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["month"] = df["created_at"].dt.to_period("M").astype(str)
        monthly = df.groupby("month").size()
        st.line_chart(monthly)

        # ---------------- CSV EXPORT ----------------
        st.subheader("⬇️ Export Data")
        st.download_button(
            "Download Predictions CSV",
            data=df.to_csv(index=False),
            file_name="predictions.csv",
            mime="text/csv"
        )

        st.divider()
        st.subheader("📜 All Predictions")
        st.dataframe(df, use_container_width=True)

# ==================================
# STUDENT ANALYTICS (ADMIN)
# ==================================
elif menu == "Student Analytics":
    require_admin_login()

    st.title("🔎 Student Analytics")

    student_name = st.text_input("Enter student username")

    if st.button("Load Student Analytics"):
        if not student_name.strip():
            st.warning("Please enter a student name.")
        else:
            res = requests.get(
                f"{BACKEND_URL}/history/filter",
                params={"name": student_name}
            ).json()

            df = pd.DataFrame(res["data"])

            if df.empty:
                st.info("No data found for this student.")
            else:
                st.subheader("📜 Prediction History")
                st.dataframe(df, use_container_width=True)

                st.subheader("📊 Skill Distribution")
                st.bar_chart(df["predicted_skill"].value_counts())

                st.subheader("📈 Skill Progress")
                df["created_at"] = pd.to_datetime(df["created_at"])
                df["skill_value"] = df["predicted_skill"].map({
                    "Beginner": 1,
                    "Intermediate": 2,
                    "Advanced": 3
                })
                st.line_chart(df.set_index("created_at")["skill_value"])

# ==================================
# LOGOUTS
# ==================================
st.sidebar.markdown("---")

if st.session_state.student_logged_in:
    if st.sidebar.button("🚪 Student Logout"):
        st.session_state.student_logged_in = False
        st.session_state.student_name = None
        st.rerun()

if st.session_state.admin_logged_in:
    if st.sidebar.button("🚪 Admin Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()