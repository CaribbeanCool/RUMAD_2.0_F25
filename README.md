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
4. Install [Ollama](https://ollama.ai/) and pull the `llama3.2:latest` model:

   ```bash
   ollama pull llama3.2:latest
   ```

   > **Note:** If you want to use a different model, modify the model name in `Chatbot/llm/chatollama.py`

5. Configure the database connection in `.env` file:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```
6. (Optional) To reload the database with fresh data, use the scripts in the `reload/` folder:

   ```bash
   python reload/reload_db.py --yes
   ```

   This will drop existing tables and reload them with data from CSV files in `reload/data/`.

7. Run the Flask API application:
   ```bash
   python API/main.py
   ```
8. To run the Chatbot application, navigate to the Chatbot directory and start the Flask app:
   ```bash
   streamlit run Chatbot/main.py
   ```

## Usage

To use the Chatbot application, run the UI, open your web browser and navigate to `http://localhost:8501`. You will see the Chatbot interface where you can interact with the system. The application provides various tabs to view statistics and other relevant information about the database.

### Chatbot Interaction

In the Chatbot tab, you can type your queries related to the syllabuses of various CIIC and INSO classes, and the chatbot will respond based on the data available in the PostgreSQL database via RAG.

### Statistics Tabs

The Statistics tabs provide insights and visualizations based on the data stored in the database. You can explore different metrics and trends and customize parameters as needed.
