from datetime import datetime
import logging
import logging.handlers


class Logger(object):
    _logger = logging.getLogger('py-build-server')
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    _logger.addHandler(handler)

    def __init__(self, identifier):
        self.identifier = identifier

    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        self._logger.info(msg)

    def warn(self, msg):
        self._logger.warn(msg)

    def error(self, msg):
        self._logger.error(msg)

    def log(self, msg, severity=''):
        print('[{}] py-build-server [{}] {}: {}'.format(
              datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.identifier, severity, msg))