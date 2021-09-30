#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-variable

# Owned
__author__ = "Frederic Spiers"
__credits__ = ["Frederic Spiers", "-", "-"]
__license__ = "----"
__version__ = "6.0.0"
__date__ = "30/09/2021"
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
import skopeolib
import toolbox
from colorama import init, Fore, Back, Style

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_A

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

def parse():
    parser = argparse.ArgumentParser(prog='skopeoTransfer', description='Transfer docker image(s) from one repository to another with skopeo')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    sub_img = subparsers.add_parser('img', help='Single named image transfer mode')
    sub_file = subparsers.add_parser('file', help='Multiple transfer mode from file')
    sub_update = subparsers.add_parser('update', help='Update transfer mode')
    # GENERAL arguments
    parser.add_argument('--format', type=str, default='v2s2', choices=['v2s2', 'v2s1', 'oci'], help='Manifest type (oci, v2s1, or v2s2) to use in the destination (default is manifest type of source, with fallbacks)')
    parser.add_argument('--creds', type=str, default='credentials.json', help='Path of the json file for registries credentials')
    parser.add_argument('--safe', default=False, action='store_true', help='Using safe mode will download and upload image instead of direct transfer')
    parser.add_argument('--debug', default=False, action='store_true', help='Print out information to debug commands')
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

def set_global_parameters(global_params):
    for param in global_params:
        if not os.environ.get(param):
            print(f'{Fore.CYAN}{Style.BRIGHT}[ SKOPEO PARAMETERS ] > Global parameter {param} not defined, using default : {Fore.RED}{globals()[param]}.')
        else:
            globals()[param] = os.environ.get(param)
            print(f'{Fore.CYAN}{Style.BRIGHT}[ SKOPEO PARAMETERS ] > Specific parameter for {param} provided and set : {Fore.RED}{globals()[param]}.')

def set_manifest_format(args):
    if not os.environ.get('FORMAT'):
        print(f"{Fore.CYAN}{Style.BRIGHT}[ SKOPEO PARAMETERS ] > No custom manifest format version provided, using default : {Fore.RED}{getattr(args, 'format')}.")
    else:
        setattr(args, 'format', os.environ.get('FORMAT'))
        print(f"{Fore.CYAN}{Style.BRIGHT}[ SKOPEO PARAMETERS ] > Specific manifest format version provided and set : {Fore.RED}{getattr(args, 'format')}.")
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
    if toolbox.check_regex(tag, globals()[TAG_POLICY]):
        print(f'{Fore.GREEN}{Style.BRIGHT}[ VERSION COMPLY ] >>{Style.NORMAL} Version {Style.BRIGHT}{tag}{Style.NORMAL} is valid.')
        return tag
    else:
        print(f'{Fore.RED}{Style.BRIGHT}[ VERSION ERROR ] >>{Style.NORMAL} Version : {tag} is not valid.')
        return None

def check_latest_tag(tags_list):
    for tag in tags_list:
        if toolbox.check_regex(tag, latest_img):
            return True
        else:
            pass

def sort_version(version_nb):
    try:
        return version.Version(version_nb)
    except version.InvalidVersion as e:
        print(f'{Fore.RED}{Style.BRIGHT}[ SORT ERROR ] >> Skopeo FAILED to parse version : {version_nb} (not in PEP-440 scheme). {e}.')
        sys.exit(1)

def get_tags(img, source, release=None):
    if source.get("name") == "docker-hub":
        src_img = f'{img}'
        tags_list = skopeolib.skopeo_list_img_tags(src_img, None, release)
    else:
        src_img = f'{source.get("registry")}/{source.get("ns")}/{img}'
        tags_list = skopeolib.skopeo_list_img_tags(src_img, source, release)

    if len(tags_list) >= 1:
        str_tags_list = toolbox.convert_bytes_list_to_clean_str_list(tags_list)
        cleaned_tags = map(lambda x: comply_tag(str_tags_list[x]), range(0, len(str_tags_list), 1))
        purged_tags = filter(None, cleaned_tags)
        final_tags_list = list(purged_tags)
        if len(final_tags_list) == 0:
            print(f'{Fore.RED}{Style.BRIGHT}[ ABORTING ] >> no available tags for image {img} ({release})')
            sys.exit(1)
        if len(final_tags_list) == 1:
            tag = final_tags_list[0]
            return tag
        else:
            tags = final_tags_list
            return tags
    elif len(tags_list) == 0:
        print(f'{Fore.RED}{Style.BRIGHT}[ ABORTING ] >> There are no image version for {img} ({release})')
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
        print(f'{Fore.MAGENTA}{Style.BRIGHT}[ LISTING ] >>{Style.NORMAL} Multiple versions available for {Style.BRIGHT}{img}{Style.NORMAL} --> {Style.BRIGHT}{sorted_version}')
        print(f'{Fore.MAGENTA}{Style.BRIGHT}[ SORTING ] >> {img} {Style.NORMAL}latest tag is {Style.BRIGHT}{img}:{sorted_version[-1]}')
        return f'{img}:{sorted_version[-1]}'
    elif type(cleaned_tags) is str:
        print(f'{Fore.MAGENTA}{Style.BRIGHT}[ LISTING ] >>{Style.NORMAL} Only one version available for {Style.BRIGHT}{img}')
        print(f'{Fore.MAGENTA}{Style.BRIGHT}[ SORTING ] >> {img} {Style.NORMAL} latest tag is {Style.BRIGHT}{img}:{cleaned_tags}')
        return f'{img}:{cleaned_tags}'

def update_releases(args, source, target, docker_images, release=None, safe=False):
    releases_map = map(lambda x: get_latest_release(x, source, release), docker_images)
    latest_releases = list(releases_map)
    print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] > {Style.NORMAL}LATEST RELEASES TO TRANSFER ARE {Fore.GREEN}{Style.BRIGHT}{latest_releases}')
    skopeo_multiple_transfer(latest_releases, args.src_mode, args.dst_mode, source, target, safe)

def skopeo_single_transfer(source, target, src_mode, dst_mode, image, safe=False):
    img_only = f"{image.split('/')[-1]}"
    if source.get("name") == "docker-hub":
        src_img = f'{image}'
        dst_img = f'{target.get("registry")}/{target.get("ns")}/{img_only}'
        print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] > {Style.NORMAL}COPYING SINGLE IMAGE FROM [[ {Style.BRIGHT}{src_img}{Style.NORMAL} ]] to [[ {Style.BRIGHT}{dst_img}{Style.NORMAL} ]]')
        skopeolib.skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target, safe)
    else:
        src_img = f'{source.get("registry")}/{source.get("ns")}/{image}'
        dst_img = f'{target.get("registry")}/{target.get("ns")}/{image}'
        img_only = f'{image}'
        print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] >{Style.NORMAL} COPYING SINGLE IMAGE FROM [[ {Style.BRIGHT}{src_img}{Style.NORMAL} ]] to [[ {Style.BRIGHT}{dst_img}{Style.NORMAL} ]]')
        skopeolib.skopeo_copy(src_img, dst_img, src_mode, dst_mode, source, target, safe)

def skopeo_multiple_transfer(data, src_mode, dst_mode, source, target, safe=False):
    if source.get("name") == "docker-hub":
        print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] >{Style.NORMAL} COPYING MULTIPLE IMAGES FROM [[ {Style.BRIGHT}Docker Hub{Style.NORMAL} ]] to [[ {Style.BRIGHT}{target.get("registry")}/{target.get("ns")}{Style.NORMAL} ]]')
        skopeolib.skopeo_multiple_copy(data, src_mode, dst_mode, source, target, safe)
    else:
        print(f'{Fore.BLUE}{Style.BRIGHT}[ SKOPEO ] >{Style.NORMAL}  COPYING MULTIPLE IMAGES FROM [[ {Style.BRIGHT}{source.get("registry")}/{source.get("ns")}{Style.NORMAL} ]] to [[ {Style.BRIGHT}{target.get("registry")}/{target.get("ns")}{Style.NORMAL} ]]')
        skopeolib.skopeo_multiple_copy(data, src_mode, dst_mode, source, target, safe)

def load_cred_endpoint(credentials, args, endpoint_name):
    try:
        endpoint = copy.deepcopy(credentials[getattr(args, endpoint_name)])
    except KeyError as err:
        print(f"{Fore.RED}{Style.BRIGHT}[ ERROR ] >> {err} is not a valid {endpoint_name} options. Please check your JSON credentials file.")
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
            target = load_cred_endpoint(credentials, args, 'dst')
        else:
            target = local
        update_endpoint_namespace(target, args, 'dst_ns')
        return source, target
    else:
        source = load_cred_endpoint(credentials, args, 'src')
        if is_endpoint_transport_remote(args, 'dst_mode'):
            target = load_cred_endpoint(credentials, args, 'dst')
        else:
            target = local
        update_endpoint_namespace(source, args, 'src_ns')
        update_endpoint_namespace(target, args, 'dst_ns')
        return source, target

def prepare_transfer(args, credentials):
    set_manifest_format(args)
    set_global_parameters(global_params)
    source, target = define_endpoints(credentials, args)
    set_transfer_modes(args)
    skopeolib.skopeo_version()
    return source, target

def file_transfer_process(args, credentials, source, target):
    skopeo_multiple_transfer(args.file.readlines(), args.src_mode, args.dst_mode, source, target, args.safe)

def img_transfer_process(args, credentials, source, target):
    skopeo_single_transfer(source, target, args.src_mode, args.dst_mode, args.image, args.safe)

def file_update_process(args, credentials, source, target):
    if getattr(args, 'release') is not None:
        update_releases(args, source, target, args.update, args.release, args.safe)
    else:
        update_releases(args, source, target, args.update, None, args.safe)

############################################################################
################################### Main ###################################
############################################################################

def main():
    start = timer()
    args = parse()
    init(autoreset=True)

    if getattr(args, 'debug'):
        print(f'{Fore.MAGENTA}{Style.BRIGHT}[[ DEBUG MODE ]] >{Fore.GREEN} Activated !')
        skopeolib.debug = True

    print(f'{Fore.YELLOW}{Style.BRIGHT}[ INFO ] >{Style.NORMAL} Loading {Fore.RED}{Style.BRIGHT}{args.creds}{Fore.YELLOW}{Style.NORMAL} file.')
    credentials = toolbox.load_json(args.creds)

    credentials['public'] = public
    credentials['local'] = local

    source, target = prepare_transfer(args, credentials)
    args.func(args, credentials, source, target)

    end = timer()
    print(f'{Fore.GREEN}{Style.BRIGHT}[ SKOPEO ] > Program finished. Transfer executed successfully.')
    print(f'{Fore.GREEN}{Style.BRIGHT}[ SKOPEO ] > Program total duration : {str(timedelta(seconds=end-start))}')

if __name__ == "__main__":
    main()
