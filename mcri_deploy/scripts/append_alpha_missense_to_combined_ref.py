import hail as hl

hl.init()

COMBINED_REF_DATA_HT = '/hpc/genomeref/hg38/seqr/seqr-reference-data/all_reference_data/combined_reference_data_grch38.ht'
MCRI_COMBINED_REF_DATA_HT = '/hpc/genomeref/hg38/seqr/seqr-reference-data/all_reference_data/combined_reference_data_grch38.mcri.20231115.ht'
# COMBINED_REF_DATA_HT = '/hpc/bpipeLibrary/shared/cpipe/tools/seqr/data.20220530/seqr-reference-data/GRCh38/combined_reference_data_grch38.ht'
# MCRI_COMBINED_REF_DATA_HT = '/hpc/bpipeLibrary/shared/cpipe/tools/seqr/data.20220530/seqr-reference-data/GRCh38/combined_reference_data_grch38.mcri.20231115.ht'
ALPHA_MISSENSE_VARIANTS = (
    '/hpc/genomeref/hg38/seqr/AlphaMissense_20230919/AlphaMissense_hg38.nocopy.tsv.gz'
)

# %%
# Read Seqr combined reference data
ref_ht = hl.read_table(COMBINED_REF_DATA_HT)

am_ht = hl.import_table(
    ALPHA_MISSENSE_VARIANTS,
    force_bgz=True,
    delimiter='\t',
    impute=True,
    skip_blank_lines=True,
)
am_ht = am_ht.key_by(
    **hl.parse_variant(
        hl.str(':').join([am_ht['#CHROM'], hl.str(am_ht.POS), am_ht.REF, am_ht.ALT]),
        reference_genome='GRCh38',
    ),
)
am_ht = am_ht.drop('#CHROM', 'POS', 'REF', 'ALT')

ref_ht_with_am = ref_ht.join(am_ht, how='left')

ref_ht_with_am = ref_ht_with_am.transmute(
    alpha_missense=hl.struct(
        genome=ref_ht_with_am.genome,
        uniprot_id=ref_ht_with_am.uniprot_id,
        transcript_id=ref_ht_with_am.transcript_id,
        protein_variant=ref_ht_with_am.protein_variant,
        am_pathogenicity=ref_ht_with_am.am_pathogenicity,
        am_class=ref_ht_with_am.am_class,
    ),
)

ref_ht_with_am.write(MCRI_COMBINED_REF_DATA_HT, overwrite=True)
