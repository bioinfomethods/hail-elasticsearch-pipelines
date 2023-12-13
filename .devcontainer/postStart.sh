#!/bin/bash
#
# This script gets run everytime this devcontainer is started.

set -eo pipefail

#######################################
# info() and error() log messages to STDOUT and STDERR respectively.
# Globals:
#   None
# Arguments:
#   Variable args written out as string
# Outputs:
#   Writes message to STDOUT or STDERR
#######################################
function info() {
  echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z') INFO $(basename "$0")] $*" >&1
}

function error() {
  echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z') ERROR $(basename "$0")] $*" >&2
}

PROJECT_DIR="$(dirname $0 | xargs dirname | xargs realpath)"
info "PROJECT_DIR=$PROJECT_DIR"

source .venv/bin/activate
