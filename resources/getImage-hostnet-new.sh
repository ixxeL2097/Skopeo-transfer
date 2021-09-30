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

# v6.0.0

# SKOPEO VERSION IMAGE EXECUTED
SKOPEO_IMG=ixxel/skopeo-transfer:6.0.1-test

# STATIC VARIABLES
DEBUG=""                    # Print commands executed by script (put 'y' to activate)
SAFE=""                     # Use safe transfer mode (put 'y' to activate)
PUBLIC=""                   # Public transfer option
SOCKET=""                   # Docker daemon socket
FORMAT="v2s2"               # valid are : v2s2 (default), v2s1 or oci
TAG_POLICY=""               # Valid are : pep440 (default) or pep440_latest

# FILE TRANSFER PARAMETERS
HOST_LIST_PATH=/home/fred/Documents
LIST_FILE=list.images
CREDS_PATH=$(pwd)

# PROGRAM PARAMETERS
SUB_CMD=$1
SUB_PARAM=$2

if [[ $DEBUG = "y" ]]
then
    DEBUG='--debug'
fi
if [[ $SAFE = "y" ]]
then
    SAFE='--safe'
fi

if [[ ${!#} = "public" ]]
then
    MODE="--public"
    if [[ $SUB_CMD = "img" ]]
    then
        IMAGE=$SUB_PARAM 
        DST=$3
        DST_NS=$4
        docker run --rm -it --name skopeo --network=host \
                                          -e TAG_POLICY=$TAG_POLICY \
                                          -v $CREDS_PATH:/app:ro \
                                          $SKOPEO_IMG \
                                          $DEBUG \
                                          $SAFE \
                                          --format $FORMAT \
                                          img $IMAGE \
                                          --dst $DST \
                                          --dst-ns $DST_NS \
                                          $MODE
    elif [[ $SUB_CMD = "file" ]]
    then
        FILE_PATH=$SUB_PARAM
        DST=$3
        DST_NS=$4
        docker run --rm -it --name skopeo --network=host \
                                          -e TAG_POLICY=$TAG_POLICY \
                                          -v $CREDS_PATH:/app:ro \
                                          $SKOPEO_IMG \
                                          $DEBUG \
                                          $SAFE \
                                          --format $FORMAT \
                                          file $FILE_PATH \
                                          --dst $DST \
                                          --dst-ns $DST_NS \
                                          $MODE
    elif [[ $SUB_CMD = "update" ]]
    then
        UPDATE=${SUB_PARAM//,/ }
        DST=$3
        DST_NS=$4
        RELEASE=""
        if [[ -n $5 ]] && [[ $5 != "public" ]]
        then
            RELEASE="--release $5"
        fi
        docker run --rm -it --name skopeo --network=host \
                                          -e TAG_POLICY=$TAG_POLICY \
                                          -v $CREDS_PATH:/app:ro \
                                          $SKOPEO_IMG \
                                          $DEBUG \
                                          $SAFE \
                                          --format $FORMAT \
                                          update $UPDATE \
                                          --dst $DST \
                                          --dst-ns $DST_NS \
                                          $RELEASE \
                                          $MODE
    else
        echo "ERROR"
        exit 1
    fi
else
    if [[ $SUB_CMD = "img" ]]
    then
        IMAGE=$SUB_PARAM 
        SRC=$3
        SRC_NS=$4
        DST=$5
        DST_NS=$6
        docker run --rm -it --name skopeo --network=host \
                                          -e TAG_POLICY=$TAG_POLICY \
                                          -v $CREDS_PATH:/app:ro \
                                          $SKOPEO_IMG \
                                          $DEBUG \
                                          $SAFE \
                                          --format $FORMAT \
                                          img $IMAGE \
                                          --src $SRC \
                                          --src-ns $SRC_NS \
                                          --dst $DST \
                                          --dst-ns $DST_NS
    elif [[ $SUB_CMD = "file" ]]
    then
        FILE_PATH=$SUB_PARAM
        SRC=$3
        SRC_NS=$4
        DST=$5
        DST_NS=$6
        docker run --rm -it --name skopeo --network=host \
                                          -e TAG_POLICY=$TAG_POLICY \
                                          -v $CREDS_PATH:/app:ro \
                                          $SKOPEO_IMG \
                                          $DEBUG \
                                          $SAFE \
                                          --format $FORMAT \
                                          file $FILE_PATH \
                                          --src $SRC \
                                          --src-ns $SRC_NS \
                                          --dst $DST \
                                          --dst-ns $DST_NS
    elif [[ $SUB_CMD = "update" ]]
    then
        UPDATE=${SUB_PARAM//,/ }
        SRC=$3
        SRC_NS=$4
        DST=$5
        DST_NS=$6
        RELEASE=""
        if [[ -n $7 ]]
        then
            RELEASE="--release $7"
        fi
        docker run --rm -it --name skopeo --network=host \
                                          -e TAG_POLICY=$TAG_POLICY \
                                          -v $CREDS_PATH:/app:ro \
                                          $SKOPEO_IMG \
                                          $DEBUG \
                                          $SAFE \
                                          --format $FORMAT \
                                          update $UPDATE \
                                          --src $SRC \
                                          --src-ns $SRC_NS \
                                          --dst $DST \
                                          --dst-ns $DST_NS \
                                          $RELEASE
    else
        echo "ERROR (private)"
        exit 1
    fi
fi
