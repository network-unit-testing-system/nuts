import logging
import datetime


class Logger:
    def __init__(self):
        self.error_logger = logging.getLogger('error_log')
        self.info_logger = logging.getLogger('info_log')

        error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        error_handler = logging.FileHandler('/var/log/nuts/error.log')
        error_handler.setFormatter(error_formatter)
        self.error_logger.setLevel(logging.DEBUG)
        self.error_logger.addHandler(error_handler)
        self.error_logger.error("Begin")

        date_tag = datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
        info_formatter = logging.Formatter('%(asctime)s - %(message)s')
        info_handler = logging.FileHandler('/var/log/nuts/' + date_tag + '-testresults.log')
        info_handler.setFormatter(info_formatter)
        self.info_logger.addHandler(info_handler)
