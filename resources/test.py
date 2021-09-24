#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-variable

# Owned
__author__ = "Frederic Spiers"
__credits__ = ["Frederic Spiers", "-", "-"]
__license__ = "----"
__version__ = "5.0.0"
__date__ = "08/07/2021"
__maintainers__ = ["Frederic Spiers"]
__email1__ = "fredspiers@gmail.com"
__status__ = "Released"

############################################################################
################################## Import ##################################
############################################################################

import os
import sys
import argparse
import re
import copy
from packaging import version
from timeit import default_timer as timer
from datetime import timedelta
import json

############################################################################
################################# Variables ################################
############################################################################

# Public registry default
public = {
    "name": "docker-hub",
    "registry": "",
    "ns": ""
}
# Local docker daemon registry
daemon = {
    "name": "docker-daemon",
    "registry": "",
    "ns": ""
}

# PARAMS
global_params = ["TAG_POLICY"]
TAG_POLICY = 'pep440'

# REGEX
invisible_char = '[\\s\\t\\n]+'
# version_pattern = re.compile('^(v?[0-9]{1,2}\\.?[0-9]{0,3}\\.?[0-9]{0,3}-?[0-9]{0,4})$')
pep440_latest = re.compile('^(?:v?[0-9.-]+(r(c|ev)|a(lpha)?|b(eta)?|c|pre(view)?)?[0-9]*(\\.?(post|dev)[0-9])?|latest)$')
# pep440 = re.compile('^(v?[0-9.-]+(r(c|ev)|a(lpha)?|b(eta)?|c|pre(view)?)?[0-9]*(\\.?(post|dev)[0-9])?)$')
pep440 = re.compile('^(v?[0-9.]+-?(r(c|ev)|a(lpha)?|b(eta)?|c|pre(view)?)?[0-9]*(\\.?(post|dev)[0-9])?)$')
latest_img = re.compile('^(latest)$')

############################################################################
################################# Functions ################################
############################################################################

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    INFO = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    LOGIN = '\033[96m'
    CYAN = '\033[36m'


def test(arg):
    print("YOLO")
    print(arg)

def parse():
    parser = argparse.ArgumentParser(prog='yolo', description='Transfer docker image(s) from one repository to another with skopeo')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    sub_img = subparsers.add_parser('img', help='Single named image transfer mode')
    sub_file = subparsers.add_parser('file', help='Multiple transfer mode from file')
    sub_update = subparsers.add_parser('update', help='Update transfer mode')

    # GENERAL arguments
    parser.add_argument('--public', default=False, action='store_true', help='download from a public registry')
    parser.add_argument('--format', type=str, default='v2s2', choices=['v2s2','v2s1','oci'], help='Manifest type (oci, v2s1, or v2s2) to use in the destination (default is manifest type of source, with fallbacks)')
    parser.add_argument('--creds', type=str, default='credentials.json', help='Path of the json file for registries credentials')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    # IMG arguments
    sub_img.set_defaults(func=test)
    sub_img.add_argument('image_name', type=str, help='Name of the docker image to transfer')
    sub_img.add_argument('--src', type=str, help='source name')
    sub_img.add_argument('--dst', type=str, help='destination name')
    sub_img.add_argument('--src-ns', type=str, help='namespace for source')
    sub_img.add_argument('--dst-ns', type=str, help='namespace for destination')
    sub_img.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for source')
    sub_img.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for destination')
    # FILE arguments
    sub_file.add_argument('--src', type=str, help='source name')
    sub_file.add_argument('--dst', type=str, help='destination name')
    sub_file.add_argument('--src-ns', type=str, help='namespace for source')
    sub_file.add_argument('--dst-ns', type=str, help='namespace for destination')
    sub_file.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for destination')
    # UPDATE arguments
    sub_update.add_argument('--src', type=str, help='source name')
    sub_update.add_argument('--dst', type=str, help='destination name')
    sub_update.add_argument('--src-ns', type=str, help='namespace for source')
    sub_update.add_argument('--dst-ns', type=str, help='namespace for destination')
    sub_update.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for source')
    sub_update.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for destination')
    sub_update.add_argument('--release', type=str, help='Release of the images to update. Exemple : 3.2 will download all 3.2.x')


    # exlusive = parser.add_mutually_exclusive_group(required=True)
    # exlusive.add_argument('--image', type=str, help='Name of the docker image to transfer')
    # exlusive.add_argument('--file', type=argparse.FileType('r'), help='List of docker images to transfer. Must be a file.')
    # exlusive.add_argument('--update', nargs="*", type=str, help='Update latest img releases from one registry to another')
    # parser.add_argument('--release', type=str, help='Release of the images to update. Exemple : 3.2 will download all 3.2.x')
    
    # parser.add_argument('--src', type=str, help='source name')
    # parser.add_argument('--dst', type=str, help='destination name')
    # parser.add_argument('--src-ns', type=str, help='namespace for source')
    # parser.add_argument('--dst-ns', type=str, help='namespace for destination')
    # parser.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for source')
    # parser.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage','docker','docker-daemon','dir'], help='transport type for destination')

    args = parser.parse_args()
    args.func(args)
    return args

args = parse()
# #print(getattr(args, 'src-mode'))
# print(getattr(args, 'public'))

# for arg in vars(args):
#     print(arg, getattr(args, arg))

print(args)
print(args.command)



# if getattr(args, 'src_mode') != 'docker':
#     print("ok")
# else:
#     print("not ok")

# print(getattr(args, 'src_mode'))
# setattr(args, 'src_mode', 'wala')
# print(getattr(args, 'src_mode'))

# def set_transport_mode_format(transport_mode):
#     if transport_mode == 'docker':
#         transport_mode = f"{transport_mode}://"
#     elif transport_mode == 'dir':
#         transport_mode = f"{transport_mode}:/"
#     else:
#         transport_mode = f"{transport_mode}:"
#     print(transport_mode)

# set_transport_mode_format(getattr(args, 'src_mode'))