# Workout Tracker App

An elegant Streamlit-based workout tracker with user authentication using SQLite. Track your training sessions, monitor your progress with interactive dashboards, and analyze your workout performance over time.

## Features

- **User Authentication:** Secure login and signup with automatic redirection to the console upon successful registration.
- **Workout Logging:** Record workout sessions with details like date, day (push/pull), exercise, sets, reps, weight used, RPE, and comments.
- **Interactive Dashboard:** Visualize your progress with intuitive Plotly graphs—filter by date range and see aggregated metrics by day, week, month, or year.
- **SQLite Database:** All user credentials and workout logs are stored locally in an SQLite database.
- **Elegant Design:** A minimalist and contemplative UI built with custom CSS in Streamlit for an improved user experience.

## Installation

Ensure you have Python 3 installed on your system. Then, install the required dependencies using pip:

```bash
pip install streamlit pandas plotly
```

Clone the repository:

```bash
git clone https://github.com/sharmasaravanan/workout-tracker-app.git
cd workout-tracker-app
```

## Usage

Start the application using Streamlit:

```bash
streamlit run app.py
```

The app will launch in your browser at [http://localhost:8501](http://localhost:8501).

## Project Structure

- **app.py:**  
  The main application file. Contains all the code for user authentication, adding workout logs, and viewing the interactive dashboard.
  
- **app.db:**  
  The SQLite database file that stores user information and workout logs. This file is created automatically when you run the app.

## Customization

- **Exercise Lists:**  
  Modify the exercise options in the code to better suit your workout routine. The dropdown options for "Push Day" and "Pull Day" can be easily adjusted.

- **UI Styling:**  
  Update the custom CSS in the `app.py` file to further tailor the user interface to your preference.

- **Graphs & Analytics:**  
  Use Plotly’s expressive charting library to adjust existing graphs or introduce new visualizations that highlight different training metrics.

## Contributing

Contributions are welcome! If you'd like to improve the app or add new features, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).