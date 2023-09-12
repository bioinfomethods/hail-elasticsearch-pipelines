from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import hail as hl

if TYPE_CHECKING:
    from v03_pipeline.lib.model import ReferenceGenome

IMPUTE_SEX_ANNOTATIONS = [
    'is_female',
    'f_stat',
    'n_called',
    'expected_homs',
    'observed_homs',
    'sex',
]


XY_FSTAT_THRESHOLD: float = (
    0.75  # F-stat threshold above which a sample will be called XY.
)
XX_FSTAT_THRESHOLD: float = (
    0.5  # F-stat threshold below which a sample will be called XX
)
AAF_THRESHOLD: float = 0.05  # Alternate allele frequency threshold for `hl.impute_sex`.


class Ploidy(Enum):
    AMBIGUOUS = 'ambiguous_sex'
    ANEUPLOIDY = 'sex_aneuploidy'
    FEMALE = 'XX'
    MALE = 'XY'


def validate_contig(reference_genome: ReferenceGenome, contig: str) -> None:
    valid_contigs = {*reference_genome.autosomes, *reference_genome.sex_chromosomes}
    if contig not in valid_contigs:
        msg = f'Contig: {contig} is invalid for this reference genome'
        raise ValueError(msg)


def get_sex_expression(
    ht: hl.Table,
    use_chrY_cov: bool,  # noqa: N803
    chrY_cov_threshold: float,  # noqa: N803
) -> hl.Expression:
    sex_expression = (
        hl.case()
        .when(hl.is_missing(ht.is_female), Ploidy.AMBIGUOUS.value)
        .when(ht.is_female, Ploidy.FEMALE.value)
    )
    if use_chrY_cov:
        sex_expression = sex_expression.when(
            (
                (
                    (ht.is_female)
                    & hl.is_defined(ht.normalized_y_coverage)
                    & (ht.normalized_y_coverage > chrY_cov_threshold)
                )
                | (
                    (~ht.is_female)
                    & hl.is_defined(ht.normalized_y_coverage)
                    & (ht.normalized_y_coverage < chrY_cov_threshold)
                )
            ),
            Ploidy.ANEUPLOIDY.value,
        )
    return sex_expression.default(Ploidy.MALE.value)


def get_contig_cov(
    mt: hl.MatrixTable,
    reference_genome: ReferenceGenome,
    contig: str,
    af_field: str,
    call_rate_threshold: float,
    af_threshold: float = 0.01,
) -> hl.Table:
    """
    Calculate mean contig coverage.

    :param mt: MatrixTable containing samples with chrY variants
    :param reference_genome: ReferenceGenome, either GRCh37 or GRCh38
    :param contig: Chosen chromosome.
    :param call_rate_threshold: Minimum call rate threshold.
    :param af_threshold: Minimum allele frequency threshold. Default is 0.01
    :return: Table annotated with mean coverage of specified chromosome
    """
    validate_contig(reference_genome, contig)
    mt = hl.filter_intervals(
        mt,
        [hl.parse_locus_interval(contig, reference_genome=reference_genome.value)],
    )
    if contig == hl.get_reference(reference_genome.value).x_contigs[0]:
        mt = mt.filter_rows(mt.locus.in_x_nonpar())
    if contig == hl.get_reference(reference_genome.value).y_contigs[0]:
        mt = mt.filter_rows(mt.locus.in_y_nonpar())

    # Filter to common SNVs above defined callrate (should only have one index in the array because the MT only contains biallelic variants)
    mt = hl.variant_qc(mt)
    mt = mt.filter_rows(
        (mt.variant_qc.call_rate > call_rate_threshold) & (mt[af_field] > af_threshold),
    )
    mt = mt.select_cols(**{f'{contig}_mean_dp': hl.agg.mean(mt.DP)})
    return mt.cols()


def annotate_contig_coverages(
    mt: hl.MatrixTable,
    ht: hl.Table,
    reference_genome: ReferenceGenome,
    normalization_contig: str,
    af_field: str,
    call_rate_threshold: float,
) -> hl.Table:
    for contig in [
        normalization_contig,
        *reference_genome.sex_chromosomes,
    ]:
        contig_ht = get_contig_cov(
            mt,
            reference_genome,
            contig,
            af_field,
            call_rate_threshold,
        )
        ht = ht.annotate(**contig_ht[ht.s])
    return ht.annotate(
        normalized_y_coverage=hl.or_missing(
            ht[f'{normalization_contig}_mean_dp'] > 0,
            ht.chrY_mean_dp / ht[f'{normalization_contig}_mean_dp'],
        ),
        normalized_x_coverage=hl.or_missing(
            ht[f'{normalization_contig}_mean_dp'] > 0,
            ht.chrX_mean_dp / ht[f'{normalization_contig}_mean_dp'],
        ),
    )


def call_sex(  # noqa: PLR0913
    mt: hl.MatrixTable,
    reference_genome: ReferenceGenome,
    use_chrY_cov: bool = False,  # noqa: N803
    chrY_cov_threshold: float = 0.1,  # noqa: N803
    normalization_contig: str = 'chr20',
    af_field: str = 'info.AF',
    call_rate_threshold: float = 0.25,
) -> hl.Table:
    """
    Call sex for the samples in a given callset and export results file to the desired path.

    :param mt: MatrixTable containing samples with chrY variants
    :param reference_genome: ReferenceGenome, either GRCh37 or GRCh38
    :param use_chrY_cov: Set to True to calculate and use chrY coverage for sex inference.
        Will also compute and report chrX coverages.
        Default is False
    :param chrY_cov_threshold: Y coverage threshold used to infer sex aneuploidies.
        XY samples below and XX samples above this threshold will be inferred as having aneuploidies.
        Default is 0.1
    :param normalization_contig: Chosen chromosome for calculating normalized coverage. Default is "chr20"
    :param af_field: Name of field containing allele frequency information. Default is 'info.AF'
    :param call_rate_threshold: Minimum required call rate. Default is 0.25
    :return Table with imputed sex annotations, and the fstat plot.
    """
    validate_contig(reference_genome, normalization_contig)

    # Filter to SNVs and biallelics
    # NB: We should already have filtered biallelics, but just in case.
    mt = mt.filter_rows(hl.is_snp(mt.alleles[0], mt.alleles[1]))

    # Filter to PASS variants only (variants with empty or missing filter set)
    mt = mt.filter_rows(
        hl.is_missing(mt.filters) | (mt.filters.length() == 0),
        keep=True,
    )

    impute_sex_ht = hl.impute_sex(
        mt.GT,
        male_threshold=XY_FSTAT_THRESHOLD,
        female_threshold=XX_FSTAT_THRESHOLD,
        aaf_threshold=AAF_THRESHOLD,
    )
    ht = mt.annotate_cols(**impute_sex_ht[mt.col_key]).cols()

    annotations = IMPUTE_SEX_ANNOTATIONS
    if use_chrY_cov:
        ht = annotate_contig_coverages(
            mt,
            ht,
            reference_genome,
            normalization_contig,
            af_field,
            call_rate_threshold,
        )
        annotations = [
            *IMPUTE_SEX_ANNOTATIONS,
            f'{normalization_contig}_mean_dp',
            'chrY_mean_dp',
            'normalized_y_coverage',
            'chrX_mean_dp',
            'normalized_x_coverage',
        ]
    ht = ht.annotate(sex=get_sex_expression(ht, use_chrY_cov, chrY_cov_threshold))
    return ht.select(*annotations)
