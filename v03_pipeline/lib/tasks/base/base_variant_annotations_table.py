from __future__ import annotations

import hail as hl
import luigi

from v03_pipeline.lib.paths import (
    reference_dataset_collection_path,
    variant_annotations_table_path,
)
from v03_pipeline.lib.selects.fields import get_field_expressions
from v03_pipeline.lib.tasks.base.base_pipeline_task import BasePipelineTask
from v03_pipeline.lib.tasks.files import (
    GCSorLocalFolderTarget,
    GCSorLocalTarget,
    HailTableTask,
)


class BaseVariantAnnotationsTableTask(BasePipelineTask):
    liftover_ref_path = luigi.OptionalParameter(
        default='gs://hail-common/references/grch38_to_grch37.over.chain.gz',
        description='Path to GRCh38 to GRCh37 coordinates file',
    )

    def output(self) -> luigi.Target:
        return GCSorLocalTarget(
            variant_annotations_table_path(
                self.env,
                self.reference_genome,
                self.dataset_type,
            ),
        )

    def complete(self) -> bool:
        return GCSorLocalFolderTarget(self.output().path).exists()

    def requires(self) -> list[luigi.Task]:
        requirements = [
            HailTableTask(
                reference_dataset_collection_path(
                    self.env,
                    self.reference_genome,
                    self.dataset_type.base_reference_dataset_collection,
                ),
            ),
        ]
        for rdc in self.dataset_type.selectable_reference_dataset_collections(self.env):
            requirements.append(
                HailTableTask(
                    reference_dataset_collection_path(
                        self.env,
                        self.reference_genome,
                        rdc,
                    ),
                ),
            )
        return requirements

    def initialize_table(self) -> hl.Table:
        if self.dataset_type.base_reference_dataset_collection is None:
            key_type = self.dataset_type.table_key_type(self.reference_genome)
            ht = hl.Table.parallelize(
                [],
                key_type,
                key=key_type.fields,
            )
        else:
            ht = hl.read_table(
                reference_dataset_collection_path(
                    self.env,
                    self.reference_genome,
                    self.dataset_type.base_reference_dataset_collection,
                ),
            )
            ht = ht.annotate(**get_field_expressions(ht, **self.param_kwargs))
        return ht.annotate_globals(
            updates=hl.empty_set(hl.ttuple(hl.tstr, hl.tstr)),
        )

    def update(self, mt: hl.Table) -> hl.Table:
        return mt
