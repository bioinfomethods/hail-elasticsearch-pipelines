import hail as hl

from hail_scripts.computed_fields import variant_id, vep

from luigi_pipeline.lib.model.base_mt_schema import (
    BaseMTSchema,
    RowAnnotationOmit,
    row_annotation,
)


class BaseVariantSchema(BaseMTSchema):

    def __init__(self, mt, *args, **kwargs):
        super().__init__(mt)

    @row_annotation(disable_index=True)
    def contig(self):
        return variant_id.get_expr_for_contig(self.mt.locus)

    @row_annotation(disable_index=True)
    def start(self):
        return variant_id.get_expr_for_start_pos(self.mt)

    @row_annotation()
    def pos(self):
        return variant_id.get_expr_for_start_pos(self.mt)

    @row_annotation()
    def xpos(self):
        return variant_id.get_expr_for_xpos(self.mt.locus)

    @row_annotation(disable_index=True)
    def xstart(self):
        return variant_id.get_expr_for_xpos(self.mt.locus)

class BaseSeqrSchema(BaseVariantSchema):

    def __init__(self, *args, ref_data, interval_ref_data, clinvar_data, hgmd_data=None, **kwargs):
        self._ref_data = ref_data
        self._interval_ref_data = interval_ref_data
        self._clinvar_data = clinvar_data
        self._hgmd_data = hgmd_data

        # See _selected_ref_data
        self._selected_ref_data_cache = None

        super().__init__(*args, **kwargs)

    def set_mt(self, mt):
        super().set_mt(mt)
        # set this to None, and the @property _selected_ref_data
        # can populate it if it gets used after each MT update.
        self._selected_ref_data_cache = None

    @property
    def _selected_ref_data(self):
        """
        Reuse `self._ref_data[self.mt.row_key]` for all annotations.
        We'll use the @property _selected_ref_data to access this
        value, and lazily cache it (so as not to compute it if it
        doesn't get get accessed after an update to self.mt).

        Returns: self._ref_data[self.mt.row_key]
        """
        if not self._selected_ref_data_cache:
            self._selected_ref_data_cache = self._ref_data[self.mt.row_key]
        return self._selected_ref_data_cache

    @row_annotation()
    def vep(self):
        return self.mt.vep

    @row_annotation()
    def rsid(self):
        return self.mt.rsid

    @row_annotation()
    def filters(self):
        return self.mt.filters

    @row_annotation(name='sortedTranscriptConsequences', disable_index=True, fn_require=vep)
    def sorted_transcript_consequences(self):
        return vep.get_expr_for_vep_sorted_transcript_consequences_array(self.mt.vep)

    @row_annotation(name='docId', disable_index=True)
    def doc_id(self, length=512):
        return variant_id.get_expr_for_variant_id(self.mt, length)

    @row_annotation(name='variantId')
    def variant_id(self):
        return variant_id.get_expr_for_variant_id(self.mt)

    @row_annotation(disable_index=True)
    def end(self):
        return variant_id.get_expr_for_end_pos(self.mt)

    @row_annotation(disable_index=True)
    def ref(self):
        return variant_id.get_expr_for_ref_allele(self.mt)

    @row_annotation(disable_index=True)
    def alt(self):
        return variant_id.get_expr_for_alt_allele(self.mt)

    @row_annotation()
    def xstop(self):
        return variant_id.get_expr_for_xpos(self.mt.locus) + hl.len(variant_id.get_expr_for_ref_allele(self.mt)) - 1

    @row_annotation()
    def rg37_locus(self):
        if self.mt.locus.dtype.reference_genome.name != "GRCh38":
            raise RowAnnotationOmit
        return self.mt.rg37_locus

    @row_annotation(disable_index=True, fn_require=sorted_transcript_consequences)
    def domains(self):
        return vep.get_expr_for_vep_protein_domains_set_from_sorted(
            self.mt.sortedTranscriptConsequences)

    @row_annotation(name='transcriptConsequenceTerms', fn_require=sorted_transcript_consequences)
    def transcript_consequence_terms(self):
        return vep.get_expr_for_vep_consequence_terms_set(self.mt.sortedTranscriptConsequences)

    @row_annotation(name='transcriptIds', disable_index=True, fn_require=sorted_transcript_consequences)
    def transcript_ids(self):
        return vep.get_expr_for_vep_transcript_ids_set(self.mt.sortedTranscriptConsequences)

    @row_annotation(name='mainTranscript', disable_index=True, fn_require=sorted_transcript_consequences)
    def main_transcript(self):
        return vep.get_expr_for_worst_transcript_consequence_annotations_struct(
            self.mt.sortedTranscriptConsequences)

    @row_annotation(name='geneIds', fn_require=sorted_transcript_consequences)
    def gene_ids(self):
        return vep.get_expr_for_vep_gene_ids_set(self.mt.sortedTranscriptConsequences)

    @row_annotation(name='codingGeneIds', disable_index=True, fn_require=sorted_transcript_consequences)
    def coding_gene_ids(self):
        return vep.get_expr_for_vep_gene_ids_set(self.mt.sortedTranscriptConsequences, only_coding_genes=True)

    @row_annotation()
    def clinvar(self):
        return hl.struct(**{'allele_id': self._clinvar_data[self.mt.row_key].info.ALLELEID,
                            'clinical_significance': hl.delimit(self._clinvar_data[self.mt.row_key].info.CLNSIG),
                            'gold_stars': self._clinvar_data[self.mt.row_key].gold_stars})

    @row_annotation()
    def dbnsfp(self):
        return self._selected_ref_data.dbnsfp

class SeqrSchema(BaseSeqrSchema):
    @row_annotation(disable_index=True)
    def aIndex(self):
        return self.mt.a_index

    @row_annotation(disable_index=True)
    def wasSplit(self):
        return self.mt.was_split

    @row_annotation()
    def cadd(self):
        return self._selected_ref_data.cadd

    @row_annotation()
    def gnomad_exomes(self):
        return self._selected_ref_data.gnomad_exomes

    @row_annotation()
    def gnomad_genomes(self):
        return self._selected_ref_data.gnomad_genomes

    @row_annotation()
    def eigen(self):
        return self._selected_ref_data.eigen

    @row_annotation()
    def exac(self):
        return self._selected_ref_data.exac

    @row_annotation()
    def mpc(self):
        return self._selected_ref_data.mpc

    @row_annotation()
    def primate_ai(self):
        return self._selected_ref_data.primate_ai

    @row_annotation()
    def splice_ai(self):
        return self._selected_ref_data.splice_ai

    @row_annotation()
    def topmed(self):
        return self._selected_ref_data.topmed

    @row_annotation()
    def hgmd(self):
        if self._hgmd_data is None:
            raise RowAnnotationOmit
        return hl.struct(**{'accession': self._hgmd_data[self.mt.row_key].rsid,
                            'class': self._hgmd_data[self.mt.row_key].info.CLASS})

    @row_annotation()
    def gnomad_non_coding_constraint(self):
        if self._interval_ref_data is None:
            raise RowAnnotationOmit
        return hl.struct(
            **{
                "z_score": self._interval_ref_data.index(
                    self.mt.locus, all_matches=True
                )
                .filter(
                    lambda x: hl.is_defined(x.gnomad_non_coding_constraint["z_score"])
                )
                .gnomad_non_coding_constraint.z_score.first()
            }
        )

    @row_annotation()
    def screen(self):
        if self._interval_ref_data is None:
            raise RowAnnotationOmit
        return hl.struct(
            **{
                "region_type": self._interval_ref_data.index(
                    self.mt.locus, all_matches=True
                ).flatmap(lambda x: x.screen["region_type"])
            }
        )

class SeqrVariantSchema(SeqrSchema):

    @row_annotation(name='AC')
    def ac(self):
        return self.mt.gt_stats.AC[1]

    @row_annotation(name='AF')
    def af(self):
        return self.mt.gt_stats.AF[1]

    @row_annotation(name='AN', disable_index=True)
    def an(self):
        return self.mt.gt_stats.AN

    @row_annotation(name='homozygote_count')
    def hom_alt(self):
        return self.mt.gt_stats.homozygote_count[1]


class SeqrGenotypesSchema(BaseMTSchema):

    @row_annotation(disable_index=True)
    def genotypes(self):
        return hl.agg.collect(hl.struct(**self._genotype_fields()))

    @row_annotation(fn_require=genotypes)
    def samples_no_call(self):
        return self._genotype_filter_samples(lambda g: g.num_alt == -1)

    @row_annotation(fn_require=genotypes)
    def samples_num_alt(self, start=1, end=3, step=1):
        return hl.struct(**{
            f'{i}': self._genotype_filter_samples(lambda g: g.num_alt == i)
            for i in range(start, end, step)
        })

    @row_annotation(fn_require=genotypes)
    def samples_gq(self, start=0, end=95, step=5):
        # struct of x_to_y to a set of samples in range of x and y for gq.
        return hl.struct(**{
            f'{i}_to_{i + step}': self._genotype_filter_samples(lambda g: ((g.gq >= i) & (g.gq < i+step)))
            for i in range(start, end, step)
        })

    @row_annotation(fn_require=genotypes)
    def samples_ab(self, start=0, end=45, step=5):
        # struct of x_to_y to a set of samples in range of x and y for ab.
        return hl.struct(**{
            f'{i}_to_{i + step}': self._genotype_filter_samples(
                lambda g: ((g.num_alt == 1) & ((g.ab*100) >= i) & ((g.ab*100) < i+step))
            )
            for i in range(start, end, step)
        })

    def _num_alt(self, is_called):
        return hl.if_else(is_called, self.mt.GT.n_alt_alleles(), -1)

    def _genotype_filter_samples(self, filter):
        # Filter on the genotypes.
        return hl.set(self.mt.genotypes.filter(filter).map(lambda g: g.sample_id))

    def _genotype_fields(self):
        # Convert the mt genotype entries into num_alt, gq, ab, dp, and sample_id.
        is_called = hl.is_defined(self.mt.GT)
        return {
            'num_alt': self._num_alt(is_called),
            'gq': hl.if_else(is_called, self.mt.GQ, 0),
            'ab': hl.bind(
                lambda total: hl.if_else((is_called) & (total != 0) & (hl.len(self.mt.AD) > 1),
                                      hl.float(self.mt.AD[1] / total),
                                      hl.missing(hl.tfloat)),
                hl.sum(self.mt.AD)
            ),
            'dp': hl.if_else(is_called & hl.is_defined(self.mt.AD), hl.int(hl.min(hl.sum(self.mt.AD), 32000)), hl.missing(hl.tint)),
            'sample_id': self.mt.s
        }


class SeqrMcriVariantSchema(BaseSeqrSchema):

    @row_annotation(name='pop_mcri_AC')
    def acMcri(self):
        return self.mt.info.get('AC_MCRI', hl.missing(hl.tint))

    @row_annotation(name='pop_mcri_AN')
    def anMcri(self):
        return self.mt.info.get('AN_MCRI', hl.missing(hl.tint))

    @row_annotation(name='pop_mcri_AF')
    def afMcri(self):
        return self.mt.info.get('AF_MCRI', hl.missing(hl.tfloat))


class SeqrVariantsAndGenotypesSchema(SeqrVariantSchema, SeqrGenotypesSchema, SeqrMcriVariantSchema):
    """
    Combined variant and genotypes.
    """

    @staticmethod
    def elasticsearch_row(ds):
        """
        Prepares the mt to export using ElasticsearchClient V02.
        - Flattens nested structs
        - drops locus and alleles key

        TODO:
        - Call validate
        - when all annotations are here, whitelist fields to send instead of blacklisting.
        :return:
        """
        # Converts a mt to the row equivalent.
        if isinstance(ds, hl.MatrixTable):
            ds = ds.rows()
        if 'vep' in ds.row:
            ds = ds.drop('vep')
        key = ds.key
        # Converts nested structs into one field, e.g. {a: {b: 1}} => a.b: 1
        table = ds.flatten()
        # When flattening, the table is unkeyed, which causes problems because our row keys should not
        # be normal fields. We can also re-key, but I believe this is computational?
        # PS: row key is often locus and allele, but does not have to be
        return table.drop(*key)
