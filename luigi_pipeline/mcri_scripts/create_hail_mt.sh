hailctl dataproc submit seqr-loading-cluster \
    seqr_loading.py --pyfiles "lib,../hail_scripts" \
    SeqrVCFToMTTask --local-scheduler \
         --source-paths gs://mcri-seqr-imports/natasha_brown_18PA005703/natasha_brown_18PA005703.merge.clean.norm.grch37.vcf.bgz \
         --dest-path gs://mcri-seqr-imports/natasha_brown_18PA005703/natasha_brown_18PA005703.mt \
         --genome-version 37 \
         --sample-type WES \
         --reference-ht-path  gs://seqr-reference-data/GRCh37/all_reference_data/combined_reference_data_grch37.ht \
         --clinvar-ht-path gs://seqr-reference-data/GRCh37/clinvar/clinvar.GRCh37.ht
