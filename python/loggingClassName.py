# Set a Default for className: Modify your logger to provide a default value for className if it is not provided. 
# You can achieve this by creating a custom LoggerAdapter that adds a default className to the extra dictionary if it is missing.
import logging

class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra'].setdefault('className', 'DefaultClassName')
        return msg, kwargs

# Create a logger and set the format
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(className)s:%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Wrap the logger with the CustomAdapter
logger = CustomAdapter(logger, {})

# Now you can use logger.info without needing to provide 'className' every time
logger.info("This message has a default className")
logger.info("This message has a custom className", extra={'className': 'TT'})
