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
# classic transfer :     ./getImage-hostnet.sh img my-image:1.0 <source> <src-ns> <target> <dst-ns>
# public transfer :      ./getImage-hostnet.sh img my-image:1.0 <source> <src-ns> <target> <dst-ns> public
# file list transfer :   ./getImage-hostnet.sh file file.txt <source> <src-ns> <target> <dst-ns> 
# update latest :        ./getImage-hostnet.sh update my-image:1.0,his-image:v1.0 <source> <src-ns> <target> <dst-ns> 
# update specific :      ./getImage-hostnet.sh update my-image:1.0,his-image:v1.0 <source> <src-ns> <target> <dst-ns> 3.2
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
SKOPEO_IMG=ixxel/skopeo-transfer:6.0.0

# STATIC VARIABLES
DEBUG=""                    # Print commands executed by script (put 'y' to activate)
SAFE=""                     # Use safe transfer mode (put 'y' to activate)
PUBLIC=""                   # Public transfer option
FORMAT="v2s2"               # valid are : v2s2 (default), v2s1 or oci
TAG_POLICY=""               # Valid are : pep440 (default) or pep440_latest
SRC_TRANSPORT="docker"      # transport mode for source
DST_TRANSPORT="docker"      # transport mode for destination

# FILE TRANSFER PARAMETERS
HOST_LIST_PATH=$(pwd)

# CREDENTIALS
CREDS_PATH=$(pwd)

# DNS & PROXY PARAMETERS
USER=user
PASSWD=password
PROXY=10.55.207.1:8080/
DNS=10.55.46.157
HTTP_PROXY="http://$USER:$PASSWD@$PROXY"
HTTPS_PROXY="http://$USER:$PASSWD@$PROXY"
NOPROXY="localhost,127.0.0.1,*.example.com"

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
        CMD="img"
        PARAM=$SUB_PARAM 
        DST=$3
        DST_NS=$4
    elif [[ $SUB_CMD = "file" ]]
    then
        CMD="file"
        PARAM=$SUB_PARAM
        DST=$3
        DST_NS=$4
    elif [[ $SUB_CMD = "update" ]]
    then
        CMD="update"
        PARAM=${SUB_PARAM//,/ }
        DST=$3
        DST_NS=$4
        RELEASE=""
        if [[ -n $5 ]] && [[ $5 != "public" ]]
        then
            RELEASE="--release $5"
        fi
    else
        echo "ERROR"
        exit 1
    fi     
    docker run --rm -it --name skopeo --dns=$DNS \
                                        -e TAG_POLICY=$TAG_POLICY \
                                        -e https_proxy=$HTTP_PROXY \
                                        -e http_proxy=$HTTPS_PROXY \
                                        -e no_proxy=$NOPROXY \
                                        -v $CREDS_PATH:/app:ro \
                                        -v $HOST_LIST_PATH:/app:ro \
                                        $SKOPEO_IMG \
                                        $DEBUG \
                                        $SAFE \
                                        --format $FORMAT \
                                        $CMD $PARAM \
                                        --dst $DST \
                                        --dst-ns $DST_NS \
                                        --dst-mode $DST_TRANSPORT \
                                        $RELEASE \
                                        $MODE
else
    if [[ $SUB_CMD = "img" ]]
    then
        CMD="img"
        PARAM=$SUB_PARAM 
        SRC=$3
        SRC_NS=$4
        DST=$5
        DST_NS=$6
    elif [[ $SUB_CMD = "file" ]]
    then
        CMD="file"
        PARAM=$SUB_PARAM 
        SRC=$3
        SRC_NS=$4
        DST=$5
        DST_NS=$6
    elif [[ $SUB_CMD = "update" ]]
    then
        CMD="update"
        PARAM=${SUB_PARAM//,/ }
        SRC=$3
        SRC_NS=$4
        DST=$5
        DST_NS=$6
        RELEASE=""
        if [[ -n $7 ]]
        then
            RELEASE="--release $7"
        fi
    else
        echo "ERROR"
        exit 1
    fi
    docker run --rm -it --name skopeo --dns=$DNS \
                                        -e TAG_POLICY=$TAG_POLICY \
                                        -e https_proxy=$HTTP_PROXY \
                                        -e http_proxy=$HTTPS_PROXY \
                                        -e no_proxy=$NOPROXY \
                                        -v $CREDS_PATH:/app:ro \
                                        -v $HOST_LIST_PATH:/app:ro \
                                        $SKOPEO_IMG \
                                        $DEBUG \
                                        $SAFE \
                                        --format $FORMAT \
                                        $CMD $PARAM \
                                        --src $SRC \
                                        --src-ns $SRC_NS \
                                        --src-mode $SRC_TRANSPORT \
                                        --dst $DST \
                                        --dst-ns $DST_NS \
                                        --dst-mode $DST_TRANSPORT \
                                        $RELEASE
fi
