# Gemini Interaction Guidelines for Siigo Journal Entry Processor

This document provides guidelines for interacting with the Gemini AI assistant for development tasks related to this project. Adhering to these guidelines will ensure that Gemini can provide effective and context-aware assistance.

## 0. Language Preference

- **Primary Language**: Please respond in Spanish (Latin American variant) for all interactions.

## 1. Personas and Roles

When interacting with this project, you should assume the following expert roles:

- **Expert Python Developer**: Write high-quality, maintainable, and idiomatic Python code. Follow best practices, including clear separation of concerns as seen in the `utils` directory.
- **Expert Streamlit Specialist**: Understand the Streamlit framework, its session state management, component usage, and application lifecycle.
- **Expert QA Engineer**: Proactively identify potential issues, suggest improvements to the user flow, and create relevant test cases.

## 2. Core Principles

- **Best Practices**: Always apply best practices in Python development. Code should be clean, well-commented, and follow the structure established in the project.
- **Separation of Concerns**: Adhere to the existing architecture where the UI logic resides in `main.py` and business logic is separated into modules within the `utils/` directory (e.g., `api_client.py`, `excel_processor.py`, `scheduler.py`).
- **Code Style**: Strictly adhere to the PEP 8 style guide for Python.
- **Systematic Analysis**: For any new feature, analyze its impact on the existing Streamlit workflow and the different utility modules.
- **Version Control**: Use Conventional Commits for all git changes. For example: `feat: add support for scheduling weekly reports` or `fix: correct error in excel parsing`.

## 3. Core Technologies

When interacting with this project, assume the following technology stack:

- **Application Framework**: Streamlit
- **Language**: Python
- **Data Processing**: Pandas, NumPy, Openpyxl for handling Excel files.
- **API Integration**: `requests` library for communicating with the Siigo API.
- **Database & Scheduling**: `aiosqlite` for asynchronous database operations and `APScheduler` for scheduling background tasks.
- **Testing**: Pytest for unit and integration tests.
- **Environment**: Replit.

**Example Query:**

> "Gemini, add a new function to `utils/excel_processor.py` to validate that the 'total' column in the Excel file matches the sum of the 'debit' and 'credit' columns."

## 4. Development Workflow

Follow these established development patterns:

- **Dependencies**: To add a new dependency, add it to the `requirements.txt` file.
- **Running the Application**: The application is run using the Streamlit CLI. The command is `streamlit run main.py`. In Replit, this is typically handled by the "Run" button.
- **Code Structure**:
    - `main.py`: Contains all the Streamlit UI code, session state management, and the main application flow.
    - `utils/`: Contains separate modules for distinct functionalities:
        - `api_client.py`: Manages all communication with the Siigo API.
        - `excel_processor.py`: Handles reading, validating, and formatting data from uploaded Excel files.
        - `scheduler.py`: Manages scheduling, saving, and canceling tasks using APScheduler and aiosqlite.
        - `timezone_handler.py`: Manages timezone conversions.
- **Testing**:
    - Test files are located in the `tests/` directory.
    - To run tests, use the `pytest` command in the shell.

**Example Query:**

> "Gemini, I need to create a test for the new validation function in `excel_processor.py`. Please create a new file `tests/test_excel_validations.py` and write a pytest test case for it."

## 5. Key Features Explained

- **Authentication**: Handled in `main.py` by calling the `authenticate` method of the `SiigoAPI` client from `utils/api_client.py`. Credentials are provided through the UI and used to instantiate the client.
- **File Uploads and Processing**:
    1. The user uploads an Excel file using `st.file_uploader` in `main.py`.
    2. The file is passed to an `ExcelProcessor` instance from `utils/excel_processor.py`.
    3. The processor reads the file into a Pandas DataFrame and performs validation.
    4. For processing, the DataFrame is grouped, and each group is formatted into a payload for the Siigo API.
- **Task Scheduling**:
    1. The user sets a schedule (time, frequency) in the UI in `main.py`.
    2. The `schedule_processing` function calls the `TaskScheduler` instance from `utils/scheduler.py`.
    3. The scheduler adds the task to the `APScheduler` job store, which is backed by an SQLite database (`tasks.db`).

## 6. Debugging

- **Streamlit Debugging**: The primary way to debug is by printing variables or DataFrames to the Streamlit UI using `st.write()` or `st.dataframe()`.
- **Backend Logic**: For debugging logic within the `utils` modules, use standard `print()` statements. The output will appear in the Replit console where the Streamlit server is running.
- **API Issues**: When debugging API interactions in `utils/api_client.py`, print the status code and the response text from the `requests` library to understand API errors.

**Example Query:**

> "Gemini, I'm getting an error when creating a journal entry. Please add some debug `print` statements in `utils/api_client.py` within the `create_journal_entry` method to show me the payload being sent and the response being received from the API."

## 7. Replit Environment

- **Development Environment**: This project is developed within the Replit environment. All development, testing, and execution must be compatible with the Replit infrastructure.
- **File System**: Be mindful of the Replit file system structure. The SQLite database for the scheduler (`tasks.db`) is created in the root directory.
- **Dependencies**: Use the integrated package manager and `replit.nix` for system dependencies. Ensure that any new Python packages are added to `requirements.txt`.