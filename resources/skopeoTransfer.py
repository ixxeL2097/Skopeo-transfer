#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-variable

# Owned
__author__ = "Frederic Spiers"
__credits__ = ["Frederic Spiers", "-", "-"]
__license__ = "----"
__version__ = "6.0.0"
__date__ = "24/09/2021"
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
local = {
    "name": "local",
    "registry": "localhost",
    "ns": "default"
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
    parser = argparse.ArgumentParser(prog='skopeoTransfer', description='Transfer docker image(s) from one repository to another with skopeo')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    sub_img = subparsers.add_parser('img', help='Single named image transfer mode')
    sub_file = subparsers.add_parser('file', help='Multiple transfer mode from file')
    sub_update = subparsers.add_parser('update', help='Update transfer mode')
    # GENERAL arguments
    parser.add_argument('--format', type=str, default='v2s2', choices=['v2s2', 'v2s1', 'oci'], help='Manifest type (oci, v2s1, or v2s2) to use in the destination (default is manifest type of source, with fallbacks)')
    parser.add_argument('--creds', type=str, default='credentials.json', help='Path of the json file for registries credentials')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    # IMG arguments
    sub_img.set_defaults(func=img_transfer_process)
    sub_img.add_argument('image', type=str, help='Name of the docker image to transfer')
    sub_img.add_argument('--public', default=False, action='store_true', help='download from a public registry')
    sub_img.add_argument('--src', type=str, help='source name')
    sub_img.add_argument('--dst', type=str, help='destination name')
    sub_img.add_argument('--src-ns', type=str, help='namespace for source')
    sub_img.add_argument('--dst-ns', type=str, help='namespace for destination')
    sub_img.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage', 'docker', 'docker-daemon', 'dir'], help='transport type for source')
    sub_img.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage', 'docker', 'docker-daemon', 'dir'], help='transport type for destination')
    # FILE arguments
    sub_file.set_defaults(func=file_transfer_process)
    sub_file.add_argument('file', type=argparse.FileType('r'), help='List of docker images to transfer. Must be a file.')
    sub_file.add_argument('--public', default=False, action='store_true', help='download from a public registry')
    sub_file.add_argument('--src', type=str, help='source name')
    sub_file.add_argument('--dst', type=str, help='destination name')
    sub_file.add_argument('--src-ns', type=str, help='namespace for source')
    sub_file.add_argument('--dst-ns', type=str, help='namespace for destination')
    sub_file.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage', 'docker', 'docker-daemon', 'dir'], help='transport type for source')
    sub_file.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage', 'docker', 'docker-daemon', 'dir'], help='transport type for destination')
    # UPDATE arguments
    sub_update.set_defaults(func=file_update_process)
    sub_update.add_argument('update', nargs="+", type=str, help='Update latest img releases from one registry to another')
    sub_update.add_argument('--public', default=False, action='store_true', help='download from a public registry')
    sub_update.add_argument('--src', type=str, help='source name')
    sub_update.add_argument('--dst', type=str, help='destination name')
    sub_update.add_argument('--src-ns', type=str, help='namespace for source')
    sub_update.add_argument('--dst-ns', type=str, help='namespace for destination')
    sub_update.add_argument('--src-mode', type=str, default='docker', choices=['containers-storage', 'docker', 'docker-daemon', 'dir'], help='transport type for source')
    sub_update.add_argument('--dst-mode', type=str, default='docker', choices=['containers-storage', 'docker', 'docker-daemon', 'dir'], help='transport type for destination')
    sub_update.add_argument('--release', type=str, help='Release of the images to update. Exemple : 3.2 will download all 3.2.x')

    args = parser.parse_args()
    return args

def load_json(json_file_path):
    try:
        json_file = open(json_file_path, 'r')
        try:
            python_dict = json.load(json_file)
        except json.decoder.JSONDecodeError:
            print(f'{bcolors.FAIL}[ ERROR ] >> File {json_file_path} could not be converted to json.{bcolors.ENDC}')
            sys.exit(1)
    except IOError:
        print(f'{bcolors.FAIL}[ ERROR ] >> Failed to open file {json_file_path}.{bcolors.ENDC}')
        sys.exit(1)
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

def set_global_parameters(global_params):
    for param in global_params:
        if not os.environ.get(param):
            print(f'{bcolors.CYAN}[ SKOPEO PARAMETERS ] > Global parameter {param} not defined, using default : {globals()[param]}.{bcolors.ENDC}')
        else:
            globals()[param] = os.environ.get(param)
            print(f'{bcolors.CYAN}[ SKOPEO PARAMETERS ] > Specific parameter for {param} provided and set : {globals()[param]}.{bcolors.ENDC}')

def set_manifest_format(args):
    if not os.environ.get('FORMAT'):
        print(f"{bcolors.CYAN}[ SKOPEO PARAMETERS ] > No custom manifest format version provided, using default : {getattr(args, 'format')}.{bcolors.ENDC}")
    else:
        setattr(args, 'format', os.environ.get('FORMAT'))
        print(f"{bcolors.CYAN}[ SKOPEO PARAMETERS ] > Specific manifest format version provided and set : {getattr(args, 'format')}.{bcolors.ENDC}")
    skopeolib.manifest_version = getattr(args, 'format')

def set_transport_mode_format(transport_mode):
    if transport_mode == 'docker':
        transport_mode = f"{transport_mode}://"
    elif transport_mode == 'dir':
        transport_mode = f"{transport_mode}:/"
    else:
        transport_mode = f"{transport_mode}:"
    return transport_mode

def set_transfer_modes(args):
    setattr(args, 'src_mode', set_transport_mode_format(args.src_mode))
    setattr(args, 'dst_mode', set_transport_mode_format(args.dst_mode))

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
        #cleaned_tags = map(lambda x: comply_tag(str_tags_list[x]), range(1, len(str_tags_list) - 1, 1))
        cleaned_tags = map(lambda x: comply_tag(str_tags_list[x]), range(0, len(str_tags_list), 1))
        purged_tags = filter(None, cleaned_tags)
        final_tags_list = list(purged_tags)
        if len(final_tags_list) == 0:
            print(f'{bcolors.FAIL}[ ABORTING ] >> no available tags for image {img} ({release}){bcolors.ENDC}')
            sys.exit(1)
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
        print(f'{bcolors.HEADER}[ LISTING ] >> Multiple versions available for {img} --> {sorted_version}{bcolors.ENDC}')
        print(f'{bcolors.HEADER}[ SORTING ] >> {img} latest tag is {img}:{sorted_version[-1]}{bcolors.ENDC}')
        return f'{img}:{sorted_version[-1]}'
    elif type(cleaned_tags) is str:
        print(f'{bcolors.HEADER}[ LISTING ] >> Only one version available for {img}{bcolors.ENDC}')
        print(f'{bcolors.HEADER}[ SORTING ] >> {img} latest tag is {img}:{cleaned_tags}{bcolors.ENDC}')
        return f'{img}:{cleaned_tags}'

def update_releases(args, source, target, docker_images, release=None):
    releases_map = map(lambda x: get_latest_release(x, source, release), docker_images)
    latest_releases = list(releases_map)
    print(f'{bcolors.OKBLUE}[ SKOPEO ] > LATEST RELEASES TO TRANSFER ARE {latest_releases}{bcolors.ENDC}')
    skopeo_multiple_transfer(latest_releases, args.src_mode, args.dst_mode, source, target)

def skopeo_single_transfer(source, target, src_mode, dst_mode, image):
    img_split = image.split('/')
    img_only = f'{img_split[-1]}'
    if source.get("name") == "docker-hub":
        src_img = f'{image}'
        dst_img = f'{target.get("registry")}/{target.get("ns")}/{img_only}'
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING SINGLE IMAGE FROM [[ {src_img} ]] to [[ {dst_img} ]]{bcolors.ENDC}')
        skopeolib.skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target)
    else:
        src_img = f'{source.get("registry")}/{source.get("ns")}/{image}'
        dst_img = f'{target.get("registry")}/{target.get("ns")}/{image}'
        img_only = f'{image}'
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING SINGLE IMAGE FROM [[ {src_img} ]] to [[ {dst_img} ]]{bcolors.ENDC}')
        skopeolib.skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target)

def skopeo_multiple_transfer(data, src_mode, dst_mode, source, target):
    if source.get("name") == "docker-hub":
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING MULTIPLE IMAGES FROM [[ Docker Hub ]] to [[ {target.get("registry")}/{target.get("ns")} ]]{bcolors.ENDC}')
        skopeolib.skopeo_multiple_copy(data, src_mode, dst_mode, source, target)
    else:
        print(f'{bcolors.OKBLUE}[ SKOPEO ] > COPYING MULTIPLE IMAGES FROM [[ {source.get("registry")}/{source.get("ns")} ]] to [[ {target.get("registry")}/{target.get("ns")} ]]{bcolors.ENDC}')
        skopeolib.skopeo_multiple_copy(data, src_mode, dst_mode, source, target)

def load_cred_endpoint(credentials, args, endpoint_name):
    try:
        endpoint = credentials[getattr(args, endpoint_name)]
    except KeyError as err:
        print(f"{bcolors.FAIL}[ ERROR ] >> {err} is not a valid {endpoint_name} options. Please check your JSON credentials file.{bcolors.ENDC}")
        sys.exit(1)
    return endpoint

def is_endpoint_transport_remote(args, endpoint_mode_name):
    if getattr(args, endpoint_mode_name) == 'docker-daemon' or getattr(args, endpoint_mode_name) == 'containers-storage' or getattr(args, endpoint_mode_name) == 'dir':
        return False
    else:
        return True

def update_endpoint_namespace(endpoint, args, value):
    if getattr(args, value) is not None:
        endpoint.update({'ns': getattr(args, value)})

def define_endpoints(credentials, args):
    if getattr(args, 'public'):
        source = public
        if is_endpoint_transport_remote(args, 'dst_mode'):
            print(f'{bcolors.HEADER}[ DEBUG - IMG ] > PUBLIC --> PRIVATE {bcolors.ENDC}')
            target = load_cred_endpoint(credentials, args, 'dst')
        else:
            print(f'{bcolors.HEADER}[ DEBUG - IMG ] > PUBLIC --> LOCAL {bcolors.ENDC}')
            target = local
        update_endpoint_namespace(target, args, 'dst_ns')
        return source, target
    else:
        source = load_cred_endpoint(credentials, args, 'src')
        if is_endpoint_transport_remote(args, 'dst_mode'):
            print(f'{bcolors.HEADER}[ DEBUG - IMG ] > PRIVATE --> PRIVATE {bcolors.ENDC}')
            target = load_cred_endpoint(credentials, args, 'dst')
        else:
            print(f'{bcolors.HEADER}[ DEBUG - IMG ] > PRIVATE --> LOCAL {bcolors.ENDC}')
            target = local
        update_endpoint_namespace(source, args, 'src_ns')
        update_endpoint_namespace(target, args, 'dst_ns')
        return source, target

def file_transfer_process(args, credentials, source, target):
    skopeo_multiple_transfer(args.file.readlines(), args.src_mode, args.dst_mode, source, target)

def img_transfer_process(args, credentials, source, target):
    skopeo_single_transfer(source, target, args.src_mode, args.dst_mode, args.image)

def file_update_process(args, credentials, source, target):
    if getattr(args, 'release') is not None:
        update_releases(args, source, target, args.update, args.release)
    else:
        update_releases(args, source, target, args.update)

def prepare_transfer(args, credentials):
    set_manifest_format(args)
    set_global_parameters(global_params)
    source, target = define_endpoints(credentials, args)
    set_transfer_modes(args)
    skopeolib.skopeo_version()
    return source, target

############################################################################
################################### Main ###################################
############################################################################

def main():
    start = timer()
    args = parse()

    print(f'{bcolors.INFO}[ INFO ] > Loading {args.creds} file.{bcolors.ENDC}')
    credentials = load_json(args.creds)

    credentials['public'] = public
    credentials['local'] = local

    # set_manifest_format(args)
    # set_global_parameters(global_params)
    # source, target = define_endpoints(credentials, args)
    # set_transfer_modes(args)

    # skopeolib.skopeo_version()
    source, target = prepare_transfer(args, credentials)
    args.func(args, credentials, source, target)

    end = timer()
    print(f'{bcolors.OKGREEN}[ SKOPEO ] > Program finished. Transfer executed successfully.{bcolors.ENDC}')
    print(f'{bcolors.OKGREEN}[ SKOPEO ] > Program total duration : {str(timedelta(seconds=end-start))}{bcolors.ENDC}')

if __name__ == "__main__":
    main()
