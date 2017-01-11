import logging
import datetime


class Logger:
    def __init__(self):
        self.errorlogger = logging.getLogger('error_log')
        self.infologger = logging.getLogger('info_log')

        errorformatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        errorhandler = logging.FileHandler('/var/log/nuts/error.log')
        errorhandler.setFormatter(errorformatter)
        self.errorlogger.setLevel(logging.DEBUG)
        self.errorlogger.addHandler(errorhandler)
        self.errorlogger.error("Begin")

        dateTag = datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
        infoformatter = logging.Formatter('%(asctime)s - %(message)s')
        infohandler = logging.FileHandler('/var/log/nuts/' + dateTag + '-testresults.log')
        infohandler.setFormatter(infoformatter)
        self.infologger.addHandler(infohandler)


