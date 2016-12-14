import logging
import datetime

class Logger:

    def __init__(self):
        self.errorlogger = logging.getLogger('nuts_error_log')
        self.inforlogger = logging.getLogger('nuts_info_log')

        errorformatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        errorhandler = logging.FileHandler('/var/log/nuts/error.log')
        errorhandler.setFormatter(errorformatter)
        self.errorlogger.addHandler(errorhandler)

        dateTag = datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
        infoformatter = logging.Formatter('%(asctime)s - %(message)s')
        infohandler = logging.FileHandler('/var/log/nuts/' + dateTag + '-testresults.log')
        infohandler.setFormatter(infoformatter)
        self.inforlogger.addHandler(infohandler)

