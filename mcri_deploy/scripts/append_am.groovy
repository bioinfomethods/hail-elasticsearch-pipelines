append_am = {
    exec """

    set -o pipefail

    module unload python || true

    source $ARCHIE_HOME/archie-cli/scripts/activate-archie.sh

    python append_alpha_missense_to_combined_ref.py | tee $output.append_am.txt

  """, "hail_pipeline"
}

run {
    append_am
}
