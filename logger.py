import logging

# Configure logging
logging.basicConfig(
    filename='app.log',  # Specify the file where logs will be saved
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(user)s - %(message)s - %(table)s',  # Specify the log message format
    datefmt='%Y-%m-%d %H:%M:%S',  # Specify the date format
    encoding='utf-8'
)