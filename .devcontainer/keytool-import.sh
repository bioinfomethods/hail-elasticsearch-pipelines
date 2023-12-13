#!/bin/bash

# Use this script to import certificate into JVM keystore, handy when switching JVMs using tools like SDKMAN.

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

if [ "$CONTAINER_IMAGE_MODE" = "mcri" ]; then
    if [[ -z "$SSL_CERT_FILE" ]]; then
        error "SSL_CERT_FILE must be set"
        exit 3
    fi

    if [[ -z "$JAVA_HOME" ]]; then
        error "JAVA_HOME must be set"
        exit 3
    fi

    if [[ -z "$JVM_KEYSTORE_PWD" ]]; then
        error "JVM_KEYSTORE_PWD must be set"
        exit 3
    fi

    if [[ -f "$JAVA_HOME/jre/lib/security/cacerts" ]]; then
        JVM_KEYSTORE_PATH="$JAVA_HOME/jre/lib/security/cacerts"
    elif [[ -f "$JAVA_HOME/lib/security/cacerts" ]]; then
        JVM_KEYSTORE_PATH="$JAVA_HOME/lib/security/cacerts"
    else
        error "Java certificates not found."
        exit 3
    fi

    set +e
    keytool -list -keystore "$JVM_KEYSTORE_PATH" -storepass "${JVM_KEYSTORE_PWD}" > /dev/null
    RESULT=$?
    set -e

    if [ $RESULT -ne 0 ]; then
        info "Access to keystore failed, most likely because this is your first time accessing the keystore and JVM_KEYSTORE_PWD password is incorrect, using default password to change password to JVM_KEYSTORE_PWD."
        keytool -v -storepasswd -noprompt -storepass changeit \
            -new "${JVM_KEYSTORE_PWD}" \
            -keystore "$JVM_KEYSTORE_PATH"
        info "Successfully changed keystore ("$JVM_KEYSTORE_PATH") password to JVM_KEYSTORE_PWD"
    fi

    set +e
    keytool -delete -alias zscaler_root -keystore "$JVM_KEYSTORE_PATH" -storepass "${JVM_KEYSTORE_PWD}"
    set -e

    keytool \
        -import -noprompt \
        -trustcacerts -alias zscaler_root \
        -file "$SSL_CERT_FILE" \
        -keystore "$JVM_KEYSTORE_PATH" \
        -storepass "${JVM_KEYSTORE_PWD}"
    
else
    info "Skip importing MCRI Zscaler root certificate to java certificate store"
fi
