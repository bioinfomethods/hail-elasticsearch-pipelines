python3 seqr_loading.py SeqrMTToESTask --local-scheduler \
    --source-paths  gs://mcri-seqr-imports/natasha_brown_18PA005703/natasha_brown_18PA005703.merge.clean.norm.grch37.vcf.bgz \
    --genome-version 37 \
    --sample-type WES \
    --dest-path gs://mcri-seqr-imports/natasha_brown_18PA005703/natasha_brown_18PA005703.mt \
    --reference-ht-path  gs://seqr-reference-data/GRCh37/all_reference_data/combined_reference_data_grch37.ht \
    --clinvar-ht-path gs://seqr-reference-data/GRCh37/clinvar/clinvar.GRCh37.ht \
    --es-host seqr.mcri.edu.au:20000/es \
    --es-index new-es-index-name \
    --es-index-min-num-shards 3

#    --source-paths  gs://seqr-datasets/GRCh37/1kg/1kg.vcf.gz \
#    --dest-path gs://mcri-seqr-imports/1kg/1kg.mt \

