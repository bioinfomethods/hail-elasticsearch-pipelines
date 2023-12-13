HPC_SHARED="/hpc/bpipeLibrary/shared"
ARCHIE_HOME="$HPC_SHARED/archie-test"

append_am = {
    exec """

    set -o pipefail

    module unload python || true

    source $ARCHIE_HOME/archie-cli/scripts/activate-archie.sh

    export PYSPARK_SUBMIT_ARGS='--driver-memory 64g --executor-memory 48g --conf spark.network.timeout=10000000 pyspark-shell'

    python append_alpha_missense_to_combined_ref.py | tee $output.append_am_finished.txt

  """, "hail_pipeline"
}

run {
    append_am
}
