# Productivity and Wellness App

## Description
The Productivity and Wellness App is a comprehensive and personalized platform that integrates productivity tools, wellness tracking, financial monitoring, and positive mental reinforcement into one unified experience. In an age of fragmented tools and apps, this app centralizes life-management features into one convenient and efficient platform.

## Purpose
This app is designed to:
- Boost productivity with task management, calendar scheduling, reminders, and daily/weekly/monthly productivity reports.
- Improve health and wellness with hydration alerts, exercise notifications, and activity logs.
- Help users manage finances by tracking expenses, setting budgets, and visualizing spending trends.
- Promote positivity with daily affirmations to support mental well-being.
-Encourage healthy eating with a built-in food tracking feature.

## Value
- Saves time by combining multiple features in one place.
- Improves quality of life by promoting balance across productivity, health, and financial well-being.
- Encourages responsible spending.
- Offers visual insights through dashboards and interactive charts.
- Offers a customizable, user-centered experience.

## Technologies Used
- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Database: SQLite
- Visualization: Plotly, Matplotlib
- Task Scheduling: APScheduler
- External APIs: Affirmation and Workout Plan APIs

## Setup Instructions

1. Clone the Repository:
   ```
   git clone https://github.com/engariba/productivity-wellness-app.git
   ```

2. Set up a Virtual Environment:
   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install Dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the App:
   ```
   flask run
   ```
   The app will be available at http://127.0.0.1:5000/.

Note: Ensure that FLASK_APP=app.py and FLASK_ENV=development are set in your environment variables.

## Screenshots
Screenshots demonstrating the app interface and functionality should be added to a /screenshots directory.

## YouTube Video Link
Watch the project demo at: https://youtu.be/BFtFzrEzUWo

## Data Science/AI Features (Extra Credit)
- Daily productivity reports are generated using data visualization libraries such as Plotly/Matplotlib.
- Expense Tracker uses data visualization to help users understand their spending patterns by category and over time—this helps with    budgeting and financial decision-making.
- Affirmation generator fetches and displays motivational quotes daily via an external API.
- Gym workouts generator fetches and displays workout plans via an external API
- Food Tracker Insights supports dietary awareness and healthy choices.

Download .exe version: https://drive.google.com/file/d/186_wY0vk7xHFNNLjCxnMGXQN3i-yp_5V/view?usp=sharing
