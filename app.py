# app.py
import sqlite3
import datetime
import hashlib

import streamlit as st
import pandas as pd
import plotly.express as px

# Name of the SQLite database file
DB_NAME = "app.db"


# ────────────────────────────
# Database helper functions
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Create table for users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    # Create table for workout logs; each record is associated with a user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            day TEXT,
            exercise TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            rpe REAL,
            comments TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


# Initialize the database at startup
init_db()


# ────────────────────────────
# Authentication helper functions

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def add_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        user_id, stored_password = result
        if stored_password == hash_password(password):
            return user_id
    return None


# ────────────────────────────
# Workout log database operation

def add_log_record(user_id, date, day, exercise, sets, reps, weight, rpe, comments):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO logs (user_id, date, day, exercise, sets, reps, weight, rpe, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, date, day, exercise, sets, reps, weight, rpe, comments))
    conn.commit()
    conn.close()


# ────────────────────────────
# Authentication UI: Login and Sign Up

def login_signup():
    st.title("Welcome to Workout Tracker")
    option = st.radio("Select an option", ["Login", "Sign Up"])

    if option == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    else:
        st.subheader("Sign Up")
        # Use unique keys for these widgets
        username = st.text_input("Choose a Username", key="signup_username")
        password = st.text_input("Choose a Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        if st.button("Sign Up"):
            if password != confirm_password:
                st.error("Passwords do not match!")
            else:
                if add_user(username, password):
                    st.success("Account created successfully!")
                    # Automatically log in after successful signup
                    user_id = login_user(username, password)
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Username already exists. Please choose a different username.")


# ────────────────────────────
# Page 1 – Add Log: Form to record a new workout entry

def add_log():
    st.title(f"{st.session_state.username.capitalize()}'s Workout Log")
    st.markdown("Enter your workout details below.")

    with st.form("log_form", clear_on_submit=True):
        # Workout date (defaults to today)
        workout_date = st.date_input("Workout Date", datetime.date.today())

        # Workout day: choose between "Push Day" and "Pull Day"
        day_options = ['Day 1: Upper Body Push (Chest, Shoulders, Triceps)', 'Day 2: Lower Body + Core',
                       'Day 3: Full-Body Circuit (Metabolic Conditioning)', 'Day 4: Upper Body Pull (Back, Biceps)',
                       'Day 5: Full-Body Strength + HIIT', 'Day 6 & 7: Active Recovery/Optional Light Cardio']
        workout_day = st.selectbox("Workout Day", options=day_options)

        # Update exercise options based on the selected day
        if workout_day == 'Day 1: Upper Body Push (Chest, Shoulders, Triceps)':
            exercises = ["Barbell Bench Press", "Incline Dumbbell Press + Lateral Raises (Superset)",
                         "Overhead Barbell Press", "Cable Tricep Pushdowns + Overhead Tricep Extension (Superset)",
                         "Drop set of push-ups to failure + 10-min HIIT"]
        elif workout_day == 'Day 2: Lower Body + Core':
            exercises = ["Barbell Squats", "Romanian Deadlifts + Walking Lunges (Superset)",
                         "Leg Press (Drop Set on Final Set)",
                         "Hanging Leg Raises + Cable Woodchoppers (Superset)", "Plank Hold"]
        elif workout_day == 'Day 3: Full-Body Circuit (Metabolic Conditioning)':
            exercises = ["Circuit (4 Rounds, 60 sec rest between rounds)", "light cardio + stretching"]
        elif workout_day == 'Day 4: Upper Body Pull (Back, Biceps)':
            exercises = ["Deadlifts", "Pull-Ups + Face Pulls (Superset)", "Barbell Rows",
                         "Dumbbell Hammer Curls + EZ Bar Curls (Superset)",
                         "Drop set of bicep curls to failure + 10-min rowing machine"]
        elif workout_day == 'Day 5: Full-Body Strength + HIIT':
            exercises = ["Clean and Press", "Front Squats + Pull-Ups (Superset)", "Bench Press", "HIIT Finisher"]
        else:
            exercises = ["30-45 min brisk walk or light jog"]
        exercise_name = st.selectbox("Exercise", options=exercises)

        # Enter numeric inputs
        sets = st.number_input("Sets", min_value=1, value=3, step=1)
        reps = st.number_input("Reps", min_value=1, value=10, step=1)
        weight = st.number_input("Weight Used (kg)", min_value=0.0, value=20.0, step=0.5)
        rpe = st.number_input("RPE", min_value=1.0, max_value=10.0, value=7.0, step=0.5)
        comments = st.text_area("Comments", placeholder="Optional: additional notes...")

        submitted = st.form_submit_button("Add Log")
        if submitted:
            date_str = workout_date.strftime("%Y-%m-%d")
            user_id = st.session_state.user_id
            add_log_record(user_id, date_str, workout_day, exercise_name, sets, reps, weight, rpe, comments)
            st.success("Workout log added successfully!")


# ────────────────────────────
# Page 2 – Dashboard: Filtering options and interactive graphs
def dashboard():
    st.title("Workout Dashboard")
    st.markdown("Analyze your workout progress over time.")
    user_id = st.session_state.user_id

    # Retrieve logs for the current user
    conn = get_connection()
    query = "SELECT * FROM logs WHERE user_id = ?"
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    if df.empty:
        st.warning("No workout logs found. Please add some logs first!")
        return

    # Convert the "date" column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Sidebar filter: Date range selection
    st.sidebar.markdown("### Date Range Filter")
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)

    filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
    if filtered_df.empty:
        st.warning("No data in the selected date range.")
        return

    # Create a new column for "Volume" (calculated as sets × reps × weight)
    filtered_df["Volume"] = filtered_df["sets"] * filtered_df["reps"] * filtered_df["weight"]

    # Display summary metrics
    st.subheader("Overall Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Workouts", filtered_df.shape[0])
    with col2:
        st.metric("Total Sets", int(filtered_df["sets"].sum()))
    with col3:
        st.metric("Total Reps", int(filtered_df["reps"].sum()))
    st.markdown("---")

    # Graph 1: Weight progression over time for selected exercises
    st.subheader("Weight Progression by Exercise")
    exercise_options = list(filtered_df["exercise"].unique())
    selected_exercises = st.multiselect("Select Exercises", options=exercise_options, default=exercise_options)
    if selected_exercises:
        progress_df = filtered_df[filtered_df["exercise"].isin(selected_exercises)]
        fig_weight = px.line(
            progress_df,
            x="date",
            y="weight",
            color="exercise",
            markers=True,
            title="Weight Progression Over Time",
        )
        st.plotly_chart(fig_weight, use_container_width=True)
    else:
        st.info("Select at least one exercise to display the progress.")
    st.markdown("---")

    # Graph 2: Workout volume over time
    st.subheader("Workout Volume Over Time")
    fig_volume = px.bar(
        filtered_df,
        x="date",
        y="Volume",
        color="exercise",
        title="Workout Volume (Sets × Reps × Weight)",
    )
    st.plotly_chart(fig_volume, use_container_width=True)
    st.markdown("---")

    # Graph 3: Distribution of RPE across exercises
    st.subheader("RPE Distribution")
    fig_rpe = px.box(
        filtered_df,
        x="exercise",
        y="rpe",
        title="RPE Distribution by Exercise",
    )
    st.plotly_chart(fig_rpe, use_container_width=True)
    st.markdown("---")

    # Graph 4: Aggregated performance metrics with adjustable time intervals
    st.subheader("Aggregated Performance Metrics")
    agg_interval = st.selectbox("Select Aggregation Interval", ["Daily", "Weekly", "Monthly", "Yearly"])
    df_agg = filtered_df.copy()
    if agg_interval == "Daily":
        df_agg["Period"] = df_agg["date"].dt.date
    elif agg_interval == "Weekly":
        df_agg["Period"] = df_agg["date"].dt.to_period("W").apply(lambda r: r.start_time.date())
    elif agg_interval == "Monthly":
        df_agg["Period"] = df_agg["date"].dt.to_period("M").apply(lambda r: r.start_time.date())
    elif agg_interval == "Yearly":
        df_agg["Period"] = df_agg["date"].dt.to_period("Y").apply(lambda r: r.start_time.date())

    # Aggregated graph: maximum weight lifted per exercise in each period
    agg_weight = df_agg.groupby(["Period", "exercise"])["weight"].max().reset_index()
    fig_agg_weight = px.line(
        agg_weight,
        x="Period",
        y="weight",
        color="exercise",
        markers=True,
        title=f"Max Weight by Exercise ({agg_interval} Aggregation)",
    )
    st.plotly_chart(fig_agg_weight, use_container_width=True)

    # Aggregated graph: total workout volume per exercise in each period
    agg_volume = df_agg.groupby(["Period", "exercise"])["Volume"].sum().reset_index()
    fig_agg_volume = px.bar(
        agg_volume,
        x="Period",
        y="Volume",
        color="exercise",
        barmode="group",
        title=f"Total Volume by Exercise ({agg_interval} Aggregation)",
    )
    st.plotly_chart(fig_agg_volume, use_container_width=True)
    st.markdown("---")

    # Optionally display the raw data
    if st.checkbox("Show Raw Data"):
        st.dataframe(filtered_df.sort_values("date", ascending=False).reset_index(drop=True))


# ────────────────────────────
# Main app function with user session management and page navigation

def main():
    st.set_page_config(page_title="Workout Tracker", layout="wide")

    # Optional: add custom CSS for an elegant look
    custom_css = """
    <style>
    .reportview-container {
        background: #f5f5f5;
    }
    .sidebar .sidebar-content {
        background: #f0f0f0;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # If the user is not logged in, show the login/sign-up screen
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_signup()
        st.stop()

    # Show sidebar navigation with a welcome message and logout option
    st.sidebar.title(f"Hello, {st.session_state.username}!")
    nav = st.sidebar.radio("Navigation", ["Add Log", "Dashboard", "Logout"])

    if nav == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.sidebar.success("You have been logged out.")
        st.rerun()
    elif nav == "Add Log":
        add_log()
    elif nav == "Dashboard":
        dashboard()


if __name__ == "__main__":
    main()
