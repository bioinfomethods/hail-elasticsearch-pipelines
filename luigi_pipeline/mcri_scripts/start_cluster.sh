hailctl dataproc start \
    --pkgs luigi,google-api-python-client \
    --vep GRCh37 \
    --max-idle 30m \
    --num-workers 2 \
    --num-preemptible-workers 12 \
    seqr-loading-cluster
