# Database Project Fall 2025: RUMAD 2.0

This project is a web application built using Flask that connects to a PostgreSQL database hosted on Docker. The application allows users to interact with the database through a user-friendly interface.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

1. Clone the repository:
   ```bash
   git clone
   ```
2. Navigate to the project directory:
   ```bash
   cd rumad_2.0
   ```
3. Install the required dependencies:
   ```bash
   uv add -r requirements.txt
   ```
4. Set up the PostgreSQL database using Docker:
   ```bash
   docker-compose up -d
   ```
5. Configure the database connection in `.env` file:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```
6. Run the Flask API application:
   ```bash
   python API/main.py
   ```
7. To run the Chatbot application, navigate to the Chatbot directory and start the Flask app:
   ```bash
   streamlit run Chatbot/main.py
   ```

## Usage

1. Open your web browser and navigate to `http://localhost:5000`.
2. Use the web interface to interact with the PostgreSQL database.
3. Follow the on-screen instructions to perform various database operations.
