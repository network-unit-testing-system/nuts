import datetime
import logging

import os

from nuts.service.settings import settings


def setup_logger():
    application_logger = logging.getLogger('nuts-application')
    test_report_logger = logging.getLogger('nuts-test-report')
    validation_logger = logging.getLogger('nuts-validation')
    pepper = logging.getLogger('pepper')
    test_report_logger.setLevel(logging.DEBUG)
    application_logger.setLevel(logging.DEBUG)
    validation_logger.setLevel(logging.DEBUG)
    pepper.setLevel(logging.DEBUG)

    nuts_log_console = settings.get_variable('NUTS_LOG_CONSOLE_LEVEL', default='INFO')
    console_log_level = getattr(logging, nuts_log_console.upper())
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    test_report_logger.addHandler(console_handler)
    application_logger.addHandler(console_handler)
    validation_logger.addHandler(console_handler)
    pepper.addHandler(console_handler)

    nuts_log_file = settings.get_variable('NUTS_LOG_FILE_LEVEL', default='INFO')
    file_log_level = getattr(logging, nuts_log_file.upper())
    log_dir = settings.get_variable('NUTS_LOG_FOLDER', default=os.getcwd())

    nuts_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    nuts_handler = logging.FileHandler(os.path.join(log_dir, 'nuts.log'))
    nuts_handler.setFormatter(nuts_formatter)
    nuts_handler.setLevel(file_log_level)
    application_logger.addHandler(nuts_handler)
    test_report_logger.addHandler(nuts_handler)
    validation_logger.addHandler(nuts_handler)
    pepper.addHandler(nuts_handler)

    date_tag = datetime.datetime.now().strftime('%Y-%b-%d_%H-%M-%S')
    report_formatter = logging.Formatter('%(asctime)s - %(message)s')

    test_report_handler = logging.FileHandler(os.path.join(log_dir, 'test-report_{}.log'.format(date_tag)))
    test_report_handler.setFormatter(report_formatter)
    test_report_handler.setLevel(file_log_level)
    test_report_logger.addHandler(test_report_handler)

    validation_handler = logging.FileHandler('validation_{}.log'.format(date_tag))
    validation_handler.setFormatter(report_formatter)
    validation_logger.setLevel(file_log_level)
    validation_logger.addHandler(validation_handler)
