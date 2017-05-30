#!/usr/bin/env python2
import argparse

import colorama
import os

from nuts.application.logger import setup_logger
from nuts.application.test_controller import TestController
from nuts.application.validation_controller import ValidationController
from nuts.service.settings import settings


def is_valid_file_path(arg_parser, arg):
    if not os.path.exists(arg):
        arg_parser.error('The file {} does not exist!'.format(arg))
    else:
        return arg


def run_validation(testfile):
    validator = ValidationController(testfile)
    return validator.logic()


def run_test(testfile):
    run_validation(testfile)
    tester = TestController(testfile)
    tester.logic()
    return True


def load_settings(config_file=None, retries=None, iterations=None, debug=False):
    if config_file:
        settings.from_file(config_file)
    rv = os.environ.get('NUTS_CONFIG_FILE')
    if rv:
        settings.from_envvar(rv)

    env = ['NUTS_SALT_REST_API_URL', 'NUTS_SALT_REST_API_USERNAME', 'NUTS_SALT_REST_API_PASSWORD',
           'NUTS_SALT_REST_API_EAUTH', 'NUTS_MAX_RETRIES', 'NUTS_WAIT_ITERATIONS', 'NUTS_LOG_FILE_LEVEL',
           'NUTS_LOG_CONSOLE_LEVEL', 'NUTS_LOG_FOLDER']
    settings.from_envvar(env)

    if retries:
        settings.cfg['NUTS_MAX_RETRIES'] = retries
    if iterations:
        settings.cfg['NUTS_WAIT_ITERATIONS'] = iterations
    if debug:
        settings.cfg['NUTS_LOG_CONSOLE_LEVEL'] = 'DEBUG'
        settings.cfg['NUTS_LOG_FILE_LEVEL'] = 'DEBUG'


def main():
    colorama.init(autoreset=True)

    parser = argparse.ArgumentParser()
    parser.add_argument('testfile', type=lambda x: is_valid_file_path(parser, x),
                        help='Start with a Testfile')
    parser.add_argument('-v', '--validate', action='store_const', default=run_test, const=run_validation, dest='func',
                        help='Validates Testfile')
    parser.add_argument('-m', '--iterations', type=int, default=None,
                        help='Changes the number of iterations that nuts waits for a result')
    parser.add_argument('-r', '--retries', default=None, type=int,
                        help='Set the max retries for failed tests')
    parser.add_argument('-c', '--config', type=lambda x: is_valid_file_path(parser, x), default=None,
                        help='Config file formatted as YAML. Settings will be merged with ENVVARs')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='Debug mode vor STDOUT and log files.')

    args = parser.parse_args()
    load_settings(config_file=args.config, retries=args.retries, iterations=args.iterations, debug=args.debug)
    setup_logger()

    result = args.func(testfile=args.testfile)
    if not result:
        exit(1)


if __name__ == '__main__':
    main()
