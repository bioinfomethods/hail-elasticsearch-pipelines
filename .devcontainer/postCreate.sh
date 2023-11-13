#!/bin/bash
#
# Sets up development environment including tooling for Python, Nodejs and JVM.
#
# This script gets run after devcontainer is created.

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

git config --global user.name "$GIT_USER"
git config --global user.email "$GIT_EMAIL"

PROJECT_DIR="$(dirname $0 | xargs dirname | xargs realpath)"
info "PROJECT_DIR=$PROJECT_DIR"

info "Setting up your Python modules"
pushd "$PROJECT_DIR"

if [ "$CONTAINER_IMAGE_MODE" = "mcri" ]; then
    info "MCRI ZScaler workaround, appending SSL_CERT_FILE to REQUESTS_CA_BUNDLE"
    export PIP_ROOT_USER_ACTION=ignore
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org requests
    export REQUESTS_CA_BUNDLE="$(python3 -c 'import requests; print(requests.certs.where())')"
    info "REQUESTS_CA_BUNDLE=$REQUESTS_CA_BUNDLE"
    info "Making $REQUESTS_CA_BUNDLE writable so MCRI ZScaler certificate can be appended to it"
    chmod 666 "$REQUESTS_CA_BUNDLE"
    cat "$SSL_CERT_FILE" >> "$REQUESTS_CA_BUNDLE"
    pip install --upgrade pip setuptools

    echo -e '\nexport REQUESTS_CA_BUNDLE='"$REQUESTS_CA_BUNDLE"'\n' >>"$HOME/.bashrc"
    echo -e '\nexport REQUESTS_CA_BUNDLE='"$REQUESTS_CA_BUNDLE"'\n' >>"$HOME/.zshrc"

    # pip install -r requirements.txt
    pip install -r requirements-dev.txt

    info "MCRI ZScaler workaround complete, appended SSL_CERT_FILE to REQUESTS_CA_BUNDLE ($REQUESTS_CA_BUNDLE)"
fi

info "Setting up your JVM modules"
cp "$PROJECT_DIR/.devcontainer/keytool-import.sh" /usr/local/bin/
keytool-import.sh

if [ -f "$GCLOUD_SERVICE_ACCOUNT_KEY_FILE" ]; then
    info "Activating Google Cloud service account key file $GCLOUD_SERVICE_ACCOUNT_KEY_FILE"
    gcloud auth activate-service-account --key-file "$GCLOUD_SERVICE_ACCOUNT_KEY_FILE"
fi

# Must manually run below and follow prompts
# gcloud auth application-default login
