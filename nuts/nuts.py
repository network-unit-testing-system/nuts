#!/usr/bin/env python2
import os
import sys
import argparse
import logging
import datetime
import colorama
from src.application.Logger import Logger
from src.application.ValidationController import ValidationController
from src.application.TestController import TestController


def main(argv):
    colorama.init(autoreset=True)

    logger = Logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Start with a Testfile", nargs=1)
    parser.add_argument("-v", "--validate", help="Validates Testfile", nargs=1, )
    parser.add_argument('-its', '--iterations', help='Changes the number of iterations that nuts waits for a result',
                        nargs=1)

    args = parser.parse_args()
    if args.input:
        validator = ValidationController(os.getcwd() + "/" + args.input[0])
        if validator.logic():
            if(args.iterations):
                tester = TestController(os.getcwd() + "/" + args.input[0], max_iterations=int(args.iterations[0]))
            else:
                tester = TestController(os.getcwd() + "/" + args.input[0])
            tester.logic()
    elif args.validate:
        validator = ValidationController(os.getcwd() + "/" + args.validate[0])
        validator.logic()


if __name__ == "__main__":
        main(sys.argv[1:])
