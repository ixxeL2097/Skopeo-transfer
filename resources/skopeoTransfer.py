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
import skopeolib
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

def parse():
    parser = argparse.ArgumentParser(description='Transfer docker image(s) from one repository to another with skopeo')
    exlusive = parser.add_mutually_exclusive_group(required=True)
    exlusive.add_argument('--image', type=str, help='Name of the docker image to transfer')
    exlusive.add_argument('--file', type=argparse.FileType('r'), help='List of docker images to transfer. Must be a file.')
    exlusive.add_argument('--update', nargs="*", type=str, help='Update latest img releases from one registry to another')
    parser.add_argument('--release', type=str, help='Release of the images to update. Exemple : 3.2 will download all 3.2.x')
    parser.add_argument('--public', default=False, action='store_true', help='download from a public registry')
    parser.add_argument('--daemon', default=False, action='store_true', help='use local docker daemon registry')
    parser.add_argument('--creds', type=str, help='Path of the json file for registries credentials')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    return args

def load_json(json_file_path):
    json_file = open(json_file_path, 'r')
    python_dict = json.load(json_file)
    return python_dict

def convert_bytes_to_string(bytes):
    string = ''.join(map(chr, bytes))
    return string

def convert_bytes_list_to_clean_str_list(bytes_list):
    clean_str_list = []
    for bytes_elem in bytes_list:
        str_elem = convert_bytes_to_string(bytes_elem)
        purged_tag = re.sub('[\\s\",\\n]', '', str_elem)
        clean_str_list.append(purged_tag)
    return clean_str_list

def check_regex(string, pattern):
    if pattern.search(string):
        return True
    else:
        return False

def check_env_vars(mandatory_env_vars):
    for var in mandatory_env_vars:
        if var not in os.environ:
            raise EnvironmentError(f'{bcolors.FAIL}[ ERROR ] >> Environment variable {var} not defined. Please set {var}.{bcolors.ENDC}')
    print(f'{bcolors.OKGREEN}[ CHECK SUCCESS ] >> all ENV vars provided. Processing transfer now...{bcolors.ENDC}')

def set_global_parameters(global_params):
    for param in global_params:
        if not os.environ.get(param):
            print(f'{bcolors.CYAN}[ SKOPEO PARAMETERS ] > Global parameter {param} not defined, using default : {globals()[param]}.{bcolors.ENDC}')
        else:
            globals()[param] = os.environ.get(param)
            print(f'{bcolors.CYAN}[ SKOPEO PARAMETERS ] > Specific parameter for {param} provided and set : {globals()[param]}.{bcolors.ENDC}')

def set_manifest_format():
    if not os.environ.get('MANIFEST_FORMAT'):
        print(f'{bcolors.CYAN}[ SKOPEO PARAMETERS ] > No custom manifest format version provided, using default : {skopeolib.manifest_version}.{bcolors.ENDC}')
    else:
        skopeolib.manifest_version = os.environ.get('MANIFEST_FORMAT')
        print(f'{bcolors.CYAN}[ SKOPEO PARAMETERS ] > Specific manifest format version provided and set : {skopeolib.manifest_version}.{bcolors.ENDC}')

def set_namespaces_values(source, target):
    source.update({'ns': re.sub(invisible_char, '', str(os.environ.get('SRC_NAMESPACE')))})
    target.update({'ns': re.sub(invisible_char, '', str(os.environ.get('DST_NAMESPACE')))})

def setEnv(credentials):
    try:
        source = credentials.get(os.environ.get('SOURCE'))
        target = credentials.get(os.environ.get('TARGET'))
        # source = copy.deepcopy(globals()[os.environ.get('SOURCE')])
        # target = copy.deepcopy(globals()[os.environ.get('TARGET')])
        return source, target
    except Exception as e:
        print(f'{bcolors.FAIL}[ ERROR ] >> {str(e)} is not a valid SOURCE/TARGET environment variable. Please pick an available one or add your own in py script.{bcolors.ENDC}')
        sys.exit(1)

def comply_tag(tag):
    if check_regex(tag, globals()[TAG_POLICY]):
        print(f'{bcolors.OKGREEN}[ VERSION COMPLY ] >> Version {tag} is valid.{bcolors.ENDC}')
        return tag
    else:
        print(f'{bcolors.FAIL}[ VERSION ERROR ] >> Version : {tag} is not valid.{bcolors.ENDC}')
        return None

def check_latest_tag(tags_list):
    for tag in tags_list:
        if check_regex(tag, latest_img):
            return True
        else:
            pass

def sort_version(version_nb):
    try:
        return version.Version(version_nb)
    except version.InvalidVersion as e:
        print(f'{bcolors.FAIL}[ SORT ERROR ] >> Skopeo FAILED to parse version : {version_nb} (not in PEP-440 scheme). {e}.{bcolors.ENDC}')
        sys.exit(1)

def get_tags(img, source, release=None):
    if source.get("name") == "docker-hub":
        src_img = f'{img}'
        tags_list = skopeolib.skopeo_list_img_tags(src_img, None, release)
    else:
        src_img = f'{source.get("registry")}/{source.get("ns")}/{img}'
        tags_list = skopeolib.skopeo_list_img_tags(src_img, source, release)

    if len(tags_list) >= 1:
        str_tags_list = convert_bytes_list_to_clean_str_list(tags_list)
        cleaned_tags = map(lambda x: comply_tag(str_tags_list[x]), range(1, len(str_tags_list) - 1, 1))
        purged_tags = filter(None, cleaned_tags)
        final_tags_list = list(purged_tags)
        if len(final_tags_list) == 1:
            tag = final_tags_list[0]
            return tag
        else:
            tags = final_tags_list
            return tags
    elif len(tags_list) == 0:
        print(f'{bcolors.FAIL}[ ABORTING ] >> There are no image version for {img} ({release}){bcolors.ENDC}')
        sys.exit(1)

def get_latest_release(img, source, release=None):
    cleaned_tags = get_tags(img, source, release)
    if type(cleaned_tags) is list:
        if check_latest_tag(cleaned_tags):
            cleaned_tags.remove('latest')
            sorted_version = sorted(cleaned_tags, key=lambda x: sort_version(x))
            sorted_version.append('latest')
        else:
            sorted_version = sorted(cleaned_tags, key=lambda x: sort_version(x))
        print(f'{bcolors.HEADER}[ LISTING ] >> Multiple versions available for {img} --> {sorted_version}')
        print(f'{bcolors.HEADER}[ SORTING ] >> {img} latest tag is {img}:{sorted_version[-1]}{bcolors.ENDC}')
        return f'{img}:{sorted_version[-1]}'
    elif type(cleaned_tags) is str:
        print(f'{bcolors.HEADER}[ LISTING ] >> Only one version available for {img}')
        print(f'{bcolors.HEADER}[ SORTING ] >> {img} latest tag is {img}:{cleaned_tags}{bcolors.ENDC}')
        return f'{img}:{cleaned_tags}'

def update_releases(source, target, docker_images, release=None):
    releases_map = map(lambda x: get_latest_release(x, source, release), docker_images)
    latest_releases = list(releases_map)
    print(f'{bcolors.OKBLUE}[ SKOPEO ] > LATEST RELEASES TO TRANSFER ARE {latest_releases}{bcolors.ENDC}')
    skopeo_multiple_transfer(source, target, latest_releases)

def skopeo_single_transfer(source, target, image):
    img_split = image.split('/')
    img_only = f'{img_split[-1]}'
    if source.get("name") == "docker-hub":
        src_img = f'{image}'
        dst_img = f'{target.get("registry")}/{target.get("ns")}/{img_only}'
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING SINGLE IMAGE FROM [[ {src_img} ]] to [[ {dst_img} ]]{bcolors.ENDC}')
        skopeolib.pull_from_public_registry(src_img, img_only)
        skopeolib.skopeo_login(target)
        skopeolib.push_to_private_registry(img_only, dst_img, target)
    elif source.get("name") == "docker-daemon":
        src_img = f'{image}'
        dst_img = f'{target.get("registry")}/{target.get("ns")}/{img_only}'
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING SINGLE IMAGE FROM LOCAL DOCKER DAEMON [[ {src_img} ]] to [[ {dst_img} ]]{bcolors.ENDC}')
        skopeolib.skopeo_login(target)
        skopeolib.push_to_private_registry_from_daemon(src_img, dst_img, target)
    else:
        src_img = f'{source.get("registry")}/{source.get("ns")}/{image}'
        dst_img = f'{target.get("registry")}/{target.get("ns")}/{image}'
        img_only = f'{image}'
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING SINGLE IMAGE FROM [[ {src_img} ]] to [[ {dst_img} ]]{bcolors.ENDC}')
        skopeolib.skopeo_login(source)
        skopeolib.pull_from_private_registry(src_img, img_only, source)
        skopeolib.skopeo_login(target)
        skopeolib.push_to_private_registry(img_only, dst_img, target)

def skopeo_multiple_transfer(source, target, data):
    if source.get("name") == "docker-hub":
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING MULTIPLE IMAGES FROM [[ Docker Hub ]] to [[ {target.get("registry")}/{target.get("ns")} ]]{bcolors.ENDC}')
        skopeolib.multi_pull_from_public_registry(data)
        for key, value in enumerate(data):
            img_split = value.split('/')
            data[key] = img_split[-1]
        skopeolib.multi_push_to_private_registry(data, target)
    elif source.get("name") == "docker-daemon":
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING MULTIPLE IMAGES FROM [[ Local Docker Daemon ]] to [[ {target.get("registry")}/{target.get("ns")} ]]{bcolors.ENDC}')
        skopeolib.multi_push_to_private_registry(data, target, True)
    else:
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING MULTIPLE IMAGES FROM [[ {source.get("registry")}/{source.get("ns")} ]] to [[ {target.get("registry")}/{target.get("ns")} ]]{bcolors.ENDC}')
        skopeolib.multi_pull_from_private_registry(data, source)
        skopeolib.multi_push_to_private_registry(data, target)

def define_mandatory_vars(args):
    if getattr(args, 'public'):
        MANDATORY_ENV_VARS = ["TARGET", "DST_NAMESPACE"]
        os.environ['SOURCE'] = 'public'
    elif getattr(args, 'daemon'):
        MANDATORY_ENV_VARS = ["TARGET", "DST_NAMESPACE"]
        os.environ['SOURCE'] = 'daemon'
    else:
        MANDATORY_ENV_VARS = ["TARGET", "SOURCE", "SRC_NAMESPACE", "DST_NAMESPACE"]
    return MANDATORY_ENV_VARS

def prepare_execution(MANDATORY_ENV_VARS, credentials):
    check_env_vars(MANDATORY_ENV_VARS)
    set_manifest_format()
    set_global_parameters(global_params)
    source, target = setEnv(credentials)
    set_namespaces_values(source, target)
    return source, target

def process_options(source, target, args):
    skopeolib.skopeo_version()
    if getattr(args, 'image') is not None:
        skopeo_single_transfer(source, target, args.image)
    elif getattr(args, 'file') is not None:
        skopeo_multiple_transfer(source, target, args.file.readlines())
    elif getattr(args, 'update') is not None and source.get("name") != "docker-daemon":
        if getattr(args, 'release') is not None:
            update_releases(source, target, args.update, args.release)
        else:
            update_releases(source, target, args.update)
    else:
        print(f'{bcolors.FAIL}[ ERROR ] > Action UPDATE is not supported for local docker daemon transfer.{bcolors.ENDC}')
        sys.exit(1)


############################################################################
################################### Main ###################################
############################################################################

def main():
    start = timer()
    args = parse()

    if getattr(args, 'creds'):
        credentials = load_json(args.creds)
    else:
        credentials = load_json('credentials.json')
    credentials['public'] = public

    MANDATORY_ENV_VARS = define_mandatory_vars(args)
    source, target = prepare_execution(MANDATORY_ENV_VARS, credentials)
    process_options(source, target, args)

    end = timer()
    print(f'{bcolors.OKGREEN}[ SKOPEO ] > Program finished. Transfer executed successfully.{bcolors.ENDC}')
    print(f'{bcolors.OKGREEN}[ SKOPEO ] > Program total duration : {str(timedelta(seconds=end-start))}{bcolors.ENDC}')

if __name__ == "__main__":
    main()
