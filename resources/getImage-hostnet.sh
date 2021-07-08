#!/bin/bash

#########################################################################
#########################################################################
######################## SKOPEO WRAPPER SCRIPT ##########################
######################### NETWORK HOST VERSION ##########################
#########################################################################
#########################################################################

#######################################################################################################################################
################################################ USAGE EXAMPLES #######################################################################
#######################################################################################################################################
# classic transfer :     ./getImage-hostnet.sh <source> <src-ns> <target> <dst-ns> my-image:1.0
# public transfer :      ./getImage-hostnet.sh <target> <dst-ns> bitnami/mysql:5.7 public
# daemon transfer :      ./getImage-hostnet.sh <target> <dst-ns> skopeo-script-py:4.4.1 daemon
# file list transfer :   ./getImage-hostnet.sh <source> <src-ns> <target> <dst-ns> 
# update latest :        ./getImage-hostnet.sh <source> <src-ns> <target> <dst-ns> alpine-git,alpine-skopeo,alpine-argocd-cli
# update specific :      ./getImage-hostnet.sh <source> <src-ns> <target> <dst-ns> alpine-git, 3.2
#######################################################################################################################################

## WARNING ==> You need to have a 'credentials.json' file in your current directory. This file must contain your repositories information as per below :
# example :
# {
#     "creds1": {
#         "name": "repo",
#         "registry": "docker.io",
#         "sa": "user",
#         "token": "secret",
#         "ns": ""
#     },
#     "creds2": {
#         "name": "repo",
#         "registry": "docker.io",
#         "sa": "user",
#         "token": "secret",
#         "ns": ""
#     }
# }

# v5.0.0

# SKOPEO VERSION IMAGE EXECUTED
SKOPEO_IMG=skopeo-script-py:5.0.0

# PROGRAM PARAMETERS
SRC=$1
SRC_NS=$2
DST=$3
DST_NS=$4
IMAGE=$5
RELEASE=$6
PUBLIC=""               # Public transfer option
SOCKET=""               # Docker daemon socket
MANIFEST_FORMAT=""      # valid are : v2s2 (default), v2s1 or oci
TAG_POLICY=""           # Valid are : pep440 (default) or pep440_latest

# FILE TRANSFER PARAMETERS
HOST_LIST_PATH=/home/fred/Documents
LIST_FILE=list.images
CREDS_PATH=$(pwd)

if [[ ${!#} = "public" ]] && [[ $# -gt 2 ]]
then
    if [[ ! -z $6  ]]
    then
        echo "[ ERROR ] >> Too many arguments for 'Public' transfer mode. Please execute script without SOURCE (SRC) and SOURCE_NAMESPACE (SRC_NS) variables."
        exit 1
    else
        echo "[ INFO ] >> Processing transfer from a PUBLIC registry."
        MODE="--public"
        DST=$1
        DST_NS=$2
        IMAGE=$3
        RELEASE=$4
    fi
elif [[ ${!#} = "daemon" ]] && [[ $# -gt 2 ]]
then
    if [[ ! -z $6  ]]
    then
        echo "[ ERROR ] >> Too many arguments for 'Daemon' transfer mode. Please execute script without SOURCE (SRC) and SOURCE_NAMESPACE (SRC_NS) variables."
        exit 1
    else
        echo "[ INFO ] >> Processing transfer from local DOCKER DAEMON registry."
        MODE="--daemon"
        SOCKET="-v /var/run/docker.sock:/var/run/docker.sock"
        DST=$1
        DST_NS=$2
        IMAGE=$3
        RELEASE=$4
    fi
elif [[ ${!#} = "public" ]] || [[ ${!#} = "daemon" ]] && [[ $# -lt 3 ]]
then
    echo "[ ERROR ] >> Not enough arguments for 'Public' or 'Daemon' transfer mode."
    exit 1
elif [[ $# -lt 4 ]]
then
    echo "[ ERROR ] >> Not enough arguments for 'Private' transfer mode."
    exit 1
else
    echo "[ INFO ] >> Processing transfer from a PRIVATE registry."
fi

if [[ ! -z $IMAGE ]] && [[ $IMAGE != "public" ]] && [[ $IMAGE != "daemon" ]]
then
    if [[ ! $IMAGE =~ "," ]]
    then
        docker run --rm -it --name skopeo --network=host \
                $SOCKET \
                -e SOURCE=$SRC \
                -e SRC_NAMESPACE=$SRC_NS \
                -e DST_NAMESPACE=$DST_NS \
                -e TARGET=$DST \
                -e MANIFEST_FORMAT=$MANIFEST_FORMAT \
                -e TAG_POLICY=$TAG_POLICY \
                -v $CREDS_PATH:/app:ro \
                $SKOPEO_IMG \
                --image $IMAGE \
                $MODE
    elif [[ $IMAGE =~ "," ]]
    then
        if [[ ! -z $RELEASE ]] && [[ $RELEASE != "public" ]] && [[ $RELEASE != "daemon" ]]
        then
            IMAGES=${IMAGE//,/ }
            docker run --rm -it --name skopeo --network=host \
                    $SOCKET \
                    -e SOURCE=$SRC \
                    -e SRC_NAMESPACE=$SRC_NS \
                    -e DST_NAMESPACE=$DST_NS \
                    -e TARGET=$DST \
                    -e MANIFEST_FORMAT=$MANIFEST_FORMAT \
                    -e TAG_POLICY=$TAG_POLICY \
                    -v $CREDS_PATH:/app:ro \
                    $SKOPEO_IMG \
                    --update $IMAGES \
                    --release $RELEASE \
                    $MODE
        else
            IMAGES=${IMAGE//,/ }
            docker run --rm -it --name skopeo --network=host \
                    $SOCKET \
                    -e SOURCE=$SRC \
                    -e SRC_NAMESPACE=$SRC_NS \
                    -e DST_NAMESPACE=$DST_NS \
                    -e TARGET=$DST \
                    -e MANIFEST_FORMAT=$MANIFEST_FORMAT \
                    -e TAG_POLICY=$TAG_POLICY \
                    -v $CREDS_PATH:/app:ro \
                    $SKOPEO_IMG \
                    --update $IMAGES \
                    $MODE
        fi
    fi
elif [ -f "$HOST_LIST_PATH/$LIST_FILE" ]
then
    docker run --rm -it --name skopeo --network=host \
               $SOCKET \
               -e SOURCE=$SRC \
               -e SRC_NAMESPACE=$SRC_NS \
               -e DST_NAMESPACE=$DST_NS \
               -e TARGET=$DST \
               -v $HOST_LIST_PATH:/app/list:ro \
               -e MANIFEST_FORMAT=$MANIFEST_FORMAT \
               -e TAG_POLICY=$TAG_POLICY \
               -v $CREDS_PATH:/app:ro \
               $SKOPEO_IMG \
               --file /app/list/$LIST_FILE \
               $MODE
else
    echo "[ ERROR ] >> either image parameter $IMAGE is null, or no such file or directory $HOST_LIST_PATH/$LIST_FILE provided"
fi