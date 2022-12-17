# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
@package: logger

Generic logger module

"""
import logging
from os import chdir, getcwd, listdir, path, remove
from pprint import pprint as pp
from tornado.options import define, options

class logger(object):
    """
    @class: logger

    Generic logging functions for use with logging module.
    """
    def __init__(self):
        """ Initialize the logger class """

        script_name = path.basename(__file__)
        script_path = path.abspath(path.realpath(__file__))
        script_dir = path.split(script_path)[0]
        log_config_path = path.abspath(path.join(script_dir, 'model/logger.conf'))
        self.run = {
            'config': log_config_path,
            'run_path': getcwd(),
            'script_dir': script_dir,
            'script_name': script_name,
            'script_path': script_path,
            'user_name': getcwd().split('/')[2]
        }
        self.CRITICAL = 50
        self.FATAL = 50
        self.ERROR = 40
        self.WARNING = 30
        self.NOTICE = 20
        self.INFO = 20
        self.DEBUG = 10
        self.NOTSET = 0
        self.log_level = {
            'CRITICAL': self.CRITICAL,
            'FATAL': self.FATAL,
            'ERROR': self.ERROR,
            'WARNING': self.WARNING,
            'NOTICE': self.NOTICE,
            'INFO': self.INFO,
            'DEBUG': self.DEBUG,
            'NOTSET': self.NOTSET
        }
        define_items = list()
        define_items = ['dir_mem', 'log_level', 'file_log', 'use_mem']
        for item in define_items:
            define(item)

        options.parse_config_file(self.run['config'])
        use_mem_log_file = True if options.use_mem == 'True' else False
        if use_mem_log_file:
            self.log_file =\
                path.abspath(path.join(options.dir_mem, options.file_log))
        else:
            self.log_file =\
                path.abspath(path.join(path.dirname(path.realpath(__file__)),
                                                    options.file_log))

    def set_log_level(self, p_log_level=None):
        """
        Return an integer for use by Python logging module.

        :Args: {string} that is an index to self.log_level or None or other

        :Return: {integer} valid value from self.log_level
        """
        if p_log_level is None:
            return self.log_level['INFO']
        else:
            if p_log_level in self.log_level:
                return self.log_level[p_log_level]
            else:
                return self.log_level['NOTSET']

    def get_log_level(self, p_log_level_int):
        """
        Return string associated with specified log_level integer value
        """
        for key, val in self.log_level.items():
            if val == p_log_level_int:
                return key
        return 'UNKNOWN'

    def set_logs(self):
        """
        Set log level, log formatter and log outputs
        """
        self.log = logging.getLogger()
        self.log.setLevel(self.set_log_level(options.log_level))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logF = logging.FileHandler(self.log_file)
        logF.setLevel(self.set_log_level(options.log_level))
        logF.setFormatter(formatter)
        self.log.addHandler(logF)
        # logging.info("Log outputs defined")

    def write_log(self, msg_level, msg_text):
        """
        Write message if appropriate level
        """
        if msg_level not in self.log_level:
            ll_text = self.get_log_level(msg_level)
        else:
            ll_text = msg_level

        # print(("msg_level: ", msg_level))
        # print(("ll_text: ", ll_text))

        if ll_text in ('CRITICAL', 'FATAL'):
            logging.fatal(msg_text)
        elif ll_text == 'ERROR':
            logging.error(msg_text)
        elif ll_text == 'WARNING':
            logging.warning(msg_text)
        elif ll_text in ('NOTICE', 'INFO'):
            logging.info(msg_text)
        elif ll_text == 'DEBUG':
            logging.debug(msg_text)

    def close_logs(self):
        """
        Close log handlers
        """
        for handler in self.log.handlers:
            handler.close()
            self.log.removeFilter(handler)
