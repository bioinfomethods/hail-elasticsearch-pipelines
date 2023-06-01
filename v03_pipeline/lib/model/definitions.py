from __future__ import annotations

from enum import Enum


class AccessControl(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'


class AnnotationType(Enum):
    FORMATTING = 'FORMATTING'
    GENOTYPE_ENTRIES = 'GENOTYPE_ENTRIES'
    REFERENCE_DATASET_COLLECTION = 'REFERENCE_DATASET_COLLECTION'
    SAMPLE_LOOKUP_TABLE = 'SAMPLE_LOOKUP_TABLE'


class DataRoot(Enum):
    LOCAL_DATASETS = 'seqr-datasets'
    LOCAL_REFERENCE_DATA = 'seqr-reference-data'
    SEQR_DATASETS = 'gs://seqr-datasets'
    SEQR_LOADING_TEMP = 'gs://seqr-loading-temp'
    SEQR_REFERENCE_DATA = 'gs://seqr-reference-data'
    SEQR_REFERENCE_DATA_PRIVATE = 'gs://seqr-reference-data-private'
    SEQR_SCRATCH_TEMP = 'gs://seqr-scratch-temp'


class Env(Enum):
    DEV = 'dev'
    LOCAL = 'local'
    PROD = 'prod'
    TEST = 'test'

    @property
    def min_vcf_partitions(self):
        return {Env.TEST: 1}.get(self, 500)


class PipelineVersion(Enum):
    V02 = 'v02'
    V03 = 'v03'


class ReferenceGenome(Enum):
    GRCh37 = 'GRCh37'
    GRCh38 = 'GRCh38'

    @property
    def v02_value(self) -> str:
        return self.value[-2:]


class SampleFileType(Enum):
    BED = 'BED'
    VCF = 'VCF'


class SampleType(Enum):
    WES = 'WES'
    WGS = 'WGS'
