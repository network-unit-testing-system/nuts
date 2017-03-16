import logging
import datetime


class Logger:
    def __init__(self):
        self.error_logger = logging.getLogger('error_log')
        self.info_logger = logging.getLogger('info_log')
        self.info_logger.setLevel(logging.DEBUG)
        self.error_logger.setLevel(logging.DEBUG)
        
        error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        error_handler = logging.FileHandler('/var/log/nuts/error.log')
        error_handler.setFormatter(error_formatter)
        error_handler.setLevel(logging.ERROR)
        self.error_logger.addHandler(error_handler)
        self.error_logger.error("Begin")


        date_tag = datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
        info_formatter = logging.Formatter('%(asctime)s - %(message)s')
        info_handler = logging.FileHandler('/var/log/nuts/' + date_tag + '-testresults.log')
        info_handler.setFormatter(info_formatter)
        self.info_logger.addHandler(info_handler)
        
        debug_handler = logging.FileHandler('/var/log/nuts/' + date_tag + '-debug.log')
        debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(debug_formatter)
        self.error_logger.addHandler(debug_handler)
        self.info_logger.addHandler(debug_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.info_logger.addHandler(console_handler)
