ARG mode=mcri

FROM asia.gcr.io/mcri-01/pipeline-runner:develop as img_mcri

ONBUILD ENV SSL_CERT_FILE="/usr/local/share/ca-certificates/ZscalerRootCertificate-2048-SHA256.crt"
ONBUILD RUN curl -o "$SSL_CERT_FILE" http://repo.mcri.edu.au/ZCC/Certs/ZscalerRootCerts/ZscalerRootCertificate-2048-SHA256.crt
ONBUILD RUN update-ca-certificates
ONBUILD ENV REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"

FROM img_${mode}

ARG mode=mcri
ENV CONTAINER_IMAGE_MODE=${mode}

ARG ARG_JVM_KEYSTORE_PWD=changeit
ENV JVM_KEYSTORE_PWD=${ARG_JVM_KEYSTORE_PWD}
