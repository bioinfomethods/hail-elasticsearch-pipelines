import os
from dataclasses import dataclass
from typing import Literal

# NB: using os.environ.get inside the dataclass defaults gives a lint error.
GRCH37_TO_GRCH38_LIFTOVER_REF_PATH = os.environ.get(
    'GRCH37_TO_GRCH38_LIFTOVER_REF_PATH',
    'gs://hail-common/references/grch37_to_grch38.over.chain.gz',
)
GRCH38_TO_GRCH37_LIFTOVER_REF_PATH = os.environ.get(
    'GRCH38_TO_GRCH37_LIFTOVER_REF_PATH',
    'gs://hail-common/references/grch38_to_grch37.over.chain.gz',
)
HAIL_TMP_DIR = os.environ.get('HAIL_TMP_DIR', '/tmp')  # noqa: S108
HAIL_SEARCH_DATA_DIR = os.environ.get(
    'HAIL_SEARCH_DATA_DIR',
    '/var/seqr/seqr-hail-search-data',
)
LOADING_DATASETS_DIR = os.environ.get(
    'LOADING_DATASETS_DIR',
    '/var/seqr/seqr-loading-temp',
)
PRIVATE_REFERENCE_DATASETS_DIR = os.environ.get(
    'PRIVATE_REFERENCE_DATASETS_DIR',
    '/var/seqr/seqr-reference-data-private',
)
REFERENCE_DATASETS_DIR = os.environ.get(
    'REFERENCE_DATASETS_DIR',
    '/var/seqr/seqr-reference-data',
)
VEP_REFERENCE_DATASETS_DIR = os.environ.get(
    'VEP_REFERENCE_DATASETS_DIR',
    '/var/seqr/vep-reference-data',
)
HAIL_BACKEND_SERVICE_HOSTNAME = os.environ.get(
    'HAIL_BACKEND_SERVICE_HOSTNAME',
    'hail-search',
)
HAIL_BACKEND_SERVICE_PORT = int(os.environ.get('HAIL_BACKEND_SERVICE_PORT', '5000'))
CLINGEN_ALLELE_REGISTRY_LOGIN = os.environ.get('CLINGEN_ALLELE_REGISTRY_LOGIN', '')
CLINGEN_ALLELE_REGISTRY_PASSWORD = os.environ.get(
    'CLINGEN_ALLELE_REGISTRY_PASSWORD',
    '',
)
DEPLOYMENT_TYPE = os.environ.get('DEPLOYMENT_TYPE', 'prod')
GCLOUD_DATAPROC_SECONDARY_WORKERS = int(
    os.environ.get('GCLOUD_DATAPROC_SECONDARY_WORKERS', '5'),
)
GCLOUD_PROJECT = os.environ.get('GCLOUD_PROJECT')
GCLOUD_ZONE = os.environ.get('GCLOUD_ZONE')
GCLOUD_REGION = os.environ.get('GCLOUD_REGION')
PIPELINE_RUNNER_APP_VERSION = os.environ.get('PIPELINE_RUNNER_APP_VERSION', 'latest')

# Feature Flags
ACCESS_PRIVATE_REFERENCE_DATASETS = (
    os.environ.get('ACCESS_PRIVATE_REFERENCE_DATASETS') == '1'
)
CHECK_SEX_AND_RELATEDNESS = os.environ.get('CHECK_SEX_AND_RELATEDNESS') == '1'
EXPECT_WES_FILTERS = os.environ.get('EXPECT_WES_FILTERS') == '1'
INCLUDE_PIPELINE_VERSION_IN_PREFIX = (
    os.environ.get('INCLUDE_PIPELINE_VERSION_IN_PREFIX') == '1'
)
SHOULD_TRIGGER_HAIL_BACKEND_RELOAD = (
    os.environ.get('SHOULD_TRIGGER_HAIL_BACKEND_RELOAD') == '1'
)


@dataclass
class Env:
    ACCESS_PRIVATE_REFERENCE_DATASETS: bool = ACCESS_PRIVATE_REFERENCE_DATASETS
    CHECK_SEX_AND_RELATEDNESS: bool = CHECK_SEX_AND_RELATEDNESS
    CLINGEN_ALLELE_REGISTRY_LOGIN: str | None = CLINGEN_ALLELE_REGISTRY_LOGIN
    CLINGEN_ALLELE_REGISTRY_PASSWORD: str | None = CLINGEN_ALLELE_REGISTRY_PASSWORD
    DEPLOYMENT_TYPE: Literal['dev', 'prod'] = DEPLOYMENT_TYPE
    EXPECT_WES_FILTERS: bool = EXPECT_WES_FILTERS
    GCLOUD_DATAPROC_SECONDARY_WORKERS: str = GCLOUD_DATAPROC_SECONDARY_WORKERS
    GCLOUD_PROJECT: str | None = GCLOUD_PROJECT
    GCLOUD_ZONE: str | None = GCLOUD_ZONE
    GCLOUD_REGION: str | None = GCLOUD_REGION
    GRCH37_TO_GRCH38_LIFTOVER_REF_PATH: str = GRCH37_TO_GRCH38_LIFTOVER_REF_PATH
    GRCH38_TO_GRCH37_LIFTOVER_REF_PATH: str = GRCH38_TO_GRCH37_LIFTOVER_REF_PATH
    HAIL_BACKEND_SERVICE_HOSTNAME: str | None = HAIL_BACKEND_SERVICE_HOSTNAME
    HAIL_BACKEND_SERVICE_PORT: int = HAIL_BACKEND_SERVICE_PORT
    HAIL_TMP_DIR: str = HAIL_TMP_DIR
    HAIL_SEARCH_DATA_DIR: str = HAIL_SEARCH_DATA_DIR
    INCLUDE_PIPELINE_VERSION_IN_PREFIX: bool = INCLUDE_PIPELINE_VERSION_IN_PREFIX
    LOADING_DATASETS_DIR: str = LOADING_DATASETS_DIR
    PIPELINE_RUNNER_APP_VERSION: str = PIPELINE_RUNNER_APP_VERSION
    PRIVATE_REFERENCE_DATASETS_DIR: str = PRIVATE_REFERENCE_DATASETS_DIR
    REFERENCE_DATASETS_DIR: str = REFERENCE_DATASETS_DIR
    SHOULD_TRIGGER_HAIL_BACKEND_RELOAD: bool = SHOULD_TRIGGER_HAIL_BACKEND_RELOAD
    VEP_REFERENCE_DATASETS_DIR: str = VEP_REFERENCE_DATASETS_DIR
