from __future__ import annotations

import hail as hl
import luigi

from v03_pipeline.lib.methods.relatedness import build_relatedness_check_lookup
from v03_pipeline.lib.methods.sex_check import build_sex_check_lookup
from v03_pipeline.lib.misc.io import does_file_exist, import_pedigree, import_remap
from v03_pipeline.lib.misc.pedigree import parse_pedigree_ht_to_families
from v03_pipeline.lib.misc.sample_ids import remap_sample_ids, subset_samples
from v03_pipeline.lib.paths import remapped_and_subsetted_callset_path
from v03_pipeline.lib.tasks.base.base_write_task import BaseWriteTask
from v03_pipeline.lib.tasks.files import GCSorLocalTarget, RawFileTask
from v03_pipeline.lib.tasks.write_imported_callset import WriteImportedCallsetTask
from v03_pipeline.lib.tasks.write_relatedness_check_table import (
    WriteRelatednessCheckTableTask,
)
from v03_pipeline.lib.tasks.write_sex_check_table import WriteSexCheckTableTask


class WriteRemappedAndSubsettedCallsetTask(BaseWriteTask):
    n_partitions = 100
    callset_path = luigi.Parameter()
    project_guid = luigi.Parameter()
    project_remap_path = luigi.Parameter()
    project_pedigree_path = luigi.Parameter()
    ignore_missing_samples_when_subsetting = luigi.BoolParameter(
        default=False,
        parsing=luigi.BoolParameter.EXPLICIT_PARSING,
    )
    ignore_missing_samples_when_remapping = luigi.BoolParameter(
        default=False,
        parsing=luigi.BoolParameter.EXPLICIT_PARSING,
    )
    validate = luigi.BoolParameter(
        default=True,
        parsing=luigi.BoolParameter.EXPLICIT_PARSING,
    )

    def output(self) -> luigi.Target:
        return GCSorLocalTarget(
            remapped_and_subsetted_callset_path(
                self.reference_genome,
                self.dataset_type,
                self.callset_path,
                self.project_guid,
            ),
        )

    def requires(self) -> list[luigi.Task]:
        requirements = [
            WriteImportedCallsetTask(
                self.reference_genome,
                self.dataset_type,
                self.sample_type,
                self.callset_path,
                # NB: filters_path is explicitly passed as None here
                # to avoid carrying it throughout the rest of the pipeline.
                # Only the primary import task itself should be aware of it.
                None,
                self.validate,
            ),
            RawFileTask(self.project_pedigree_path),
        ]
        if self.dataset_type.check_sex_and_relatedness:
            requirements = [
                *requirements,
                WriteSexCheckTableTask(
                    self.reference_genome,
                    self.dataset_type,
                    self.sample_type,
                    self.callset_path,
                ),
                WriteRelatednessCheckTableTask(
                    self.reference_genome,
                    self.dataset_type,
                    self.sample_type,
                    self.callset_path,
                ),
            ]
        return requirements

    def create_table(self) -> hl.MatrixTable:
        callset_mt = hl.read_matrix_table(self.input()[0].path)
        pedigree_ht = import_pedigree(self.input()[1].path)

        # Remap, but only if the remap file is present!
        remap_lookup = hl.empty_dict(hl.tstr, hl.tstr)
        if does_file_exist(self.project_remap_path):
            project_remap_ht = import_remap(self.project_remap_path)
            callset_mt = remap_sample_ids(
                callset_mt,
                project_remap_ht,
                self.ignore_missing_samples_when_remapping,
            )
            remap_lookup = hl.dict(
                {r.s: r.seqr_id for r in project_remap_ht.collect()},
            )

        callset_samples = set(callset_mt.cols().s.collect())
        families = set(parse_pedigree_ht_to_families(pedigree_ht))
        families_failed_missing_samples = set()
        for family in families:
            if len(family.samples.keys() - callset_samples) > 0:
                families_failed_missing_samples.add(family)

        if not self.dataset_type.check_sex_and_relatedness:
            return subset_samples(
                callset_mt,
                hl.Table.parallelize(
                    [
                        {'s': sample.sample_id}
                        for family in (families - families_failed_missing_samples)
                        for sample in family.samples
                    ],
                    hl.tstruct(s=hl.dtype('str')),
                    key='s',
                ),
                self.ignore_missing_samples_when_subsetting,
            )

        sex_check_ht = hl.read_table(self.input()[2].path)
        relatedness_check_ht = hl.read_table(self.input()[3].path)
        sex_check_lookup = build_sex_check_lookup(
            sex_check_ht,
            remap_lookup,
        )
        build_relatedness_check_lookup(
            relatedness_check_ht,
            remap_lookup,
        )
        families_failed_sex_check = set()
        families_failed_relatedness_check = set()
        for family in families:
            for sample_id in family.sample_sex:
                if family.samples[sample_id].sex != sex_check_lookup[sample_id]:
                    families_failed_sex_check.add(family)
                    continue

        return subset_samples(
            callset_mt,
            hl.Table.parallelize(
                [
                    {'s': sample.sample_id}
                    for family in (
                        families
                        - families_failed_missing_samples
                        - families_failed_sex_check
                        - families_failed_relatedness_check
                    )
                    for sample in family.samples
                ],
                hl.tstruct(s=hl.dtype('str')),
                key='s',
            ),
            self.ignore_missing_samples_when_subsetting,
        )
