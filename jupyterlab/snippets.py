# %%
import hail as hl
hl.init()

# %%
# Read Seqr combined reference data
ref_ht = hl.read_table("gs://seqr-reference-data/GRCh38/all_reference_data/combined_reference_data_grch38.ht")

# %%
ref_ht.describe()
ref_ht.show()

# %%
ref_ht.count()

# %%
# Read Seqr interval combined reference data
int_ref_ht = hl.read_table("gs://seqr-reference-data/GRCh38/combined_interval_reference_data/combined_interval_reference_data.ht")

# Globals only show the metadata for the table
int_ref_ht.globals.describe()
int_ref_ht.globals.show()
datasets_first = int_ref_ht.globals.datasets.collect()[0]
print(datasets_first)

int_ref_ht.count()

# %%
# int_ref_ht only includes gnomad_non_coding_constraint.z_score, screen.region_type
int_ref_ht.describe()
int_ref_ht.show(2)

# %%
# Read Seqr clinvar
clinvar_ht = hl.read_table("gs://seqr-reference-data/GRCh38/clinvar/clinvar.GRCh38.ht")

clinvar_ht.globals.describe()
clinvar_ht.globals.show()

# %%
clinvar_ht.describe()
clinvar_ht.show(10)

# %%
# Read AlphaMissense variants

# The file annoyingly has first 3 lines as copyright and it starts with '#'.  Can't simply filter this out
# because #CHROM is the header for VCF file.

# Below command was used to create file AlphaMissense_hg38.nocopy.tsv.gz
# zcat AlphaMissense_hg38.tsv.gz | tail -n +4 | bgzip -c > AlphaMissense_hg38.nocopy.tsv.gz

# Below command was used to create file AlphaMissense_hg38.chr21.nocopy.tsv.gz
# zcat AlphaMissense_hg38.tsv.gz | tail -n +4 | grep -E "^#CHROM|^chr21" | bgzip -c > AlphaMissense_hg38.chr21.nocopy.tsv.gz

am_ht = hl.import_table(
    "/workspaces/seqr-loading-pipelines/tmp/AlphaMissense_hg38.chr21.nocopy.tsv.gz",
    force_bgz=True, 
    delimiter="\t", 
    impute=True,
    skip_blank_lines=True
)

# %%
am_ht.describe()
am_ht.show()

# %%
am_ht = am_ht.key_by(
    **hl.parse_variant(
        hl.str(':').join([am_ht['#CHROM'], hl.str(am_ht.POS), am_ht.REF, am_ht.ALT]),
        reference_genome='GRCh38'
    )
)
am_ht = am_ht.drop('#CHROM', 'POS', 'REF', 'ALT')
am_ht.describe()
am_ht.show()


# %%

# Now join am_ht with ref_ht
ref_ht_with_am = ref_ht.join(am_ht, how='left')

# %%
ref_ht_with_am.describe()
ref_ht_with_am.show()

# %%
# Now join am_ht with ref_ht
ref_ht_with_am = ref_ht_with_am.transmute(alpha_missense = hl.struct(
    genome=ref_ht_with_am.genome,
    uniprot_id=ref_ht_with_am.uniprot_id,
    transcript_id=ref_ht_with_am.transcript_id,
    protein_variant=ref_ht_with_am.protein_variant,
    am_pathogenicity=ref_ht_with_am.am_pathogenicity,
    am_class=ref_ht_with_am.am_class
))

# %%
ref_ht_with_am.describe()
ref_ht_with_am.show()

# %%
ref_ht_with_am.write("/workspaces/seqr-loading-pipelines/tmp/ref_ht_with_am.ht", overwrite=True)

# %%
# Read example seqr import table
mt = hl.read_matrix_table("gs://mcri-seqr-imports/R0029_test_project_grch38/e8e3016b455b97fe39eb6fab33caa57832b3326c/e8e3016b455b97fe39eb6fab33caa57832b3326c.mt")

# %%
mt.describe()

# %%
mt.entries().show()
# mt.globals.show()

# %%
mt.rows().show()

# %%
mt.cols().show()
# %%
mt.globals_table.describe()
