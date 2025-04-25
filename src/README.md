# Productivity and Wellness App

## Description
The **Productivity and Wellness App** is a Python-Flask-based web application designed to help users monitor and enhance their daily productivity. It offers a range of features, including task tracking, water intake monitoring, expense logging, and visual productivity reports powered by Plotly.

## Purpose
This project was developed as part of an assignment to showcase the creation of a web-based productivity application. The app aims to:
- Enable users to manage and track their tasks efficiently.
- Provide insightful visual reports on productivity.
- Track additional productivity metrics such as water intake and expenses.

## Key Features
- **Task Management** – Add, complete, and delete tasks seamlessly.  
- **Water Intake Tracker** – Monitor daily hydration levels.  
- **Expense Tracker** – Log and review expenses for better financial management.  
- **Productivity Reports** – View interactive charts for completed vs. pending tasks using Plotly.  
- **Automated Reminders** – Stay on track with scheduled notifications using APScheduler.  

## Technologies Used
- **Python (Flask)** – Backend framework for application logic.
- **Plotly** – Interactive data visualization.
- **HTML/CSS** – User interface design and layout.
- **SQLite** – Lightweight database for data storage.
- **APScheduler** – Background job scheduling for automated reminders.

## Project Structure
```
repo/
│── screenshots/         # App screenshots showcasing features
│── src/                # Source code directory
│   ├── app.py          # Main Flask application
│   ├── templates/      # HTML templates for UI
│   ├── static/         # Static files (CSS, JS, images)
│── requirements.txt    # Project dependencies
│── README.md           # Project documentation
```

## Getting Started
Follow these steps to set up and run the application:

### 1. Clone the Repository

### 2. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access the App
Open your browser and visit:
```
http://127.0.0.1:5000
```




