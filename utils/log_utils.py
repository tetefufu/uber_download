import logging

logging.basicConfig(
    filename='app.log',  # Use a file for logs
    filemode='w',
    encoding='utf-8',    # Set UTF-8 encoding
    level=logging.INFO
)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)  # Log all messages to the file

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)  # Log all messages to the console

log_format = '%(asctime)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)