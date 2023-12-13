#!/bin/bash
#
# Symlinks .env for this devcontainer if found, otherwise uses .env.template.
#
# This script gets run on host before devcontainer is created.

set -eo pipefail

#######################################
# info() and error() log messages to STDOUT and STDERR respectively.
#######################################
function info() {
    echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z') INFO $(basename "$0")] $*" >&1
}

function error() {
    echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z') ERROR $(basename "$0")] $*" >&2
}

PROJECT_DIR="$(dirname $0 | xargs dirname | xargs realpath)"
info "PROJECT_DIR=$PROJECT_DIR"

if [ ! -f "$PROJECT_DIR/.env" ] && [ -f "$PROJECT_DIR/.env.template" ]; then
    info "No existing .env file found, creating .env from .env.template"
    cp "$PROJECT_DIR/.env.template" "$PROJECT_DIR/.env"
fi

info "Linking .env for this devcontainer"
ln -sf "$PROJECT_DIR/.env" "$PROJECT_DIR/.devcontainer/.env"
