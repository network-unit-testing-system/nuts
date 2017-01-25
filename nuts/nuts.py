#!/usr/bin/env python2
import os
import sys
import argparse
import logging
import datetime
from src.application.Logger import Logger

from src.application.ValidationController import ValidationController
from src.application.TestController import TestController


def main(argv):
    logger = Logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Start with a Testfile", nargs=1)
    parser.add_argument("-v", "--validate", help="Validates Testcase and Device File", nargs=1, )

    args = parser.parse_args()
    if args.input:
        tester = TestController(os.getcwd() + "/" + args.input[0])
        tester.logic()
    elif args.validate:
        validator = ValidationController(os.getcwd() + "/" + args.validate[0])
        validator.logic()
   
if __name__ == "__main__":
        main(sys.argv[1:])