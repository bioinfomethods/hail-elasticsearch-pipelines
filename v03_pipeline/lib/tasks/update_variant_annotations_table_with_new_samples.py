from __future__ import annotations

import hail as hl
import luigi

from v03_pipeline.lib.misc.io import import_callset, import_pedigree, import_remap
from v03_pipeline.lib.misc.pedigree import samples_to_include
from v03_pipeline.lib.misc.sample_ids import (
    remap_sample_ids,
    subset_samples_and_variants,
)
from v03_pipeline.lib.model import SampleFileType, SampleType
from v03_pipeline.lib.selects.fields import get_field_expressions
from v03_pipeline.lib.tasks.base.base_variant_annotations_table import (
    BaseVariantAnnotationsTableTask,
)
from v03_pipeline.lib.tasks.files import RawFileTask, VCFFileTask
from v03_pipeline.lib.vep import run_vep


class UpdateVariantAnnotationsTableWithNewSamples(BaseVariantAnnotationsTableTask):
    sample_type = luigi.EnumParameter(enum=SampleType)
    callset_path = luigi.Parameter()
    project_remap_path = luigi.Parameter()
    project_pedigree_path = luigi.Parameter()

    dont_validate = luigi.BoolParameter(
        default=False,
        description='Disable checking whether the dataset matches the specified sample type and genome version',
    )
    ignore_missing_samples = luigi.BoolParameter(default=False)
    vep_config_json_path = luigi.OptionalParameter(
        default=None,
        description='Path of hail vep config .json file',
    )

    def requires(self) -> list[luigi.Task]:
        return [
            *super().requires(),
            VCFFileTask(self.callset_path)
            if self.dataset_type.sample_file_type == SampleFileType.VCF
            else RawFileTask(self.callset_path),
            RawFileTask(self.project_remap_path),
            RawFileTask(self.project_pedigree_path),
        ]

    def complete(self) -> bool:
        return super().complete() and hl.eval(
            hl.read_table(self.output().path).updates.contains(
                (self.callset_path, self.project_pedigree_path),
            ),
        )

    def update(self, existing_ht: hl.Table) -> hl.Table:
        # Import required files.
        callset_mt = import_callset(
            self.callset_path,
            self.reference_genome,
            self.dataset_type,
        )
        project_remap_ht = import_remap(self.project_remap_path)
        pedigree_ht = import_pedigree(self.project_pedigree_path)

        # Remap, then subset to samples & variants of interest.
        callset_mt = remap_sample_ids(callset_mt, project_remap_ht)
        sample_subset_ht = samples_to_include(pedigree_ht, callset_mt.cols())
        callset_mt = subset_samples_and_variants(
            callset_mt,
            sample_subset_ht,
            self.ignore_missing_samples,
        )

        # Split multi alleles
        if callset_mt.row_key.dtype.fields == ('locus', 'alleles'):
            callset_mt = hl.split_multi_hts(
                callset_mt.annotate_rows(
                    locus_old=callset_mt.locus,
                    alleles_old=callset_mt.alleles,
                ),
            )

        # Get new rows, annotate them with vep, transform with selects,
        # then stack onto the existing variant annotations table.
        # NB: the `unify=True` on the `union` here gives us the remainder
        # of the fields defined on the existing table but not over the new rows
        # (most importantly, the reference dataset fields).
        new_variants_mt = callset_mt.anti_join_rows(existing_ht)
        new_variants_mt = run_vep(
            new_variants_mt,
            self.env,
            self.reference_genome,
            self.dataset_type,
            self.vep_config_json_path,
        )
        new_variants_mt = new_variants_mt.select_rows(
            **get_field_expressions(new_variants_mt, **self.param_kwargs),
        )
        unioned_ht = existing_ht.union(new_variants_mt.rows(), unify=True)
        return unioned_ht.annotate_globals(
            updates=unioned_ht.updates.add(
                (self.callset_path, self.project_pedigree_path),
            ),
        )
