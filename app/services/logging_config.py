import logging
import sys

IS_LOCAL = True
formatter = logging.Formatter(
    '%(asctime)s :: %(filename)s :: %(pathname)s  :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s\
\n==================================================================\n'
)

class CustomLogger(logging.getLoggerClass()):

    def error(self, msg ,*args: tuple, **kwargs):
        # request_id = get_current_request_id()
        
        if self.isEnabledFor(logging.ERROR):
            self._log(level = logging.ERROR, msg = msg, args = args, **kwargs)
    
    def critical(self, msg ,*args, **kwargs):
        # request_id = get_current_request_id()
            
        if self.isEnabledFor(logging.CRITICAL):
            self._log(level = logging.CRITICAL, msg = msg, args = args, **kwargs)

    def warning(self, msg ,*args, **kwargs):
        # request_id = get_current_request_id()
        
        if self.isEnabledFor(logging.WARNING):
            self._log(level = logging.WARNING, msg = msg, args = args, **kwargs)
    
    def info(self, msg ,*args, **kwargs):
        # request_id = get_current_request_id()
        
        if self.isEnabledFor(logging.INFO):
            self._log(level = logging.INFO, msg = msg, args = args, **kwargs)

Logger = CustomLogger(__name__, level = logging.INFO)

if IS_LOCAL:
    ch = logging.FileHandler(filename = 'error.log')
    ch.setFormatter(formatter)

else:
    ch = logging.StreamHandler(stream = sys.stdout)
    ch.setFormatter(formatter)

Logger.addHandler(ch)