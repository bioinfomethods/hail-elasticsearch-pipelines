import hail as hl

from v03_pipeline.lib.model import ReferenceDatasetCollection
from v03_pipeline.lib.reference_data.compare_globals import (
    Globals,
    get_datasets_to_update,
)
from v03_pipeline.lib.tasks.base.base_variant_annotations_table import (
    BaseVariantAnnotationsTableTask,
)


class UpdateVariantAnnotationsTableWithUpdatedReferenceDataset(
    BaseVariantAnnotationsTableTask,
):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._datasets_to_update = []

    @property
    def reference_dataset_collections(self) -> list[ReferenceDatasetCollection]:
        return [
            rdc
            for rdc in ReferenceDatasetCollection.for_reference_genome_dataset_type(
                self.reference_genome,
                self.dataset_type,
            )
            if not rdc.requires_annotation
        ]

    def complete(self) -> bool:
        self._datasets_to_update = []

        if not super().complete():
            for rdc in self.reference_dataset_collections:
                self._datasets_to_update.extend(
                    rdc.datasets(
                        self.dataset_type,
                    ),
                )
            return False

        for rdc in self.reference_dataset_collections:
            annotations_ht_globals = Globals.from_ht(
                hl.read_table(self.output().path),
                rdc,
                self.dataset_type,
            )
            rdc_ht_globals = Globals.from_ht(
                self.rdc_annotation_dependencies[f'{rdc.value}_ht'],
                rdc,
                self.dataset_type,
            )
            self._datasets_to_update.extend(
                get_datasets_to_update(
                    rdc,
                    annotations_ht_globals,
                    rdc_ht_globals,
                    self.dataset_type,
                ),
            )
        return not self._datasets_to_update

    def update_table(self, ht: hl.Table) -> hl.Table:
        for dataset in self._datasets_to_update:
            rdc = ReferenceDatasetCollection.for_dataset(dataset, self.dataset_type)
            rdc_ht = self.rdc_annotation_dependencies[f'{rdc.value}_ht']

            if dataset in ht.row:
                ht = ht.drop(dataset)

            ht = ht.join(rdc_ht.select(dataset), 'left')

        return self.annotate_reference_dataset_collection_globals(ht)
