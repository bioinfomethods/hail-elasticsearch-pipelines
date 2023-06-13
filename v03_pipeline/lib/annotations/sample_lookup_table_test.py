import unittest

import hail as hl

from v03_pipeline.lib.annotations.sample_lookup_table import AC, AF, AN, hom


class SampleLookupTableAnnotationsTest(unittest.TestCase):
    def test_allele_count_annotations(self) -> None:
        ht = hl.Table.parallelize(
            [
                {
                    'id': 0,
                },
            ],
            hl.tstruct(
                id=hl.tint32,
            ),
            key='id',
        )
        sample_lookup_ht = hl.Table.parallelize(
            [
                {
                    'id': 0,
                    'ref_samples': hl.Struct(project_1={'a', 'c'}),
                    'het_samples': hl.Struct(project_1={'b', 'd'}),
                    'hom_samples': hl.Struct(project_1={'e', 'f'}),
                },
            ],
            hl.tstruct(
                id=hl.tint32,
                ref_samples=hl.tstruct(project_1=hl.tset(hl.tstr)),
                het_samples=hl.tstruct(project_1=hl.tset(hl.tstr)),
                hom_samples=hl.tstruct(project_1=hl.tset(hl.tstr)),
            ),
            key='id',
        )
        ht = ht.select(
            AC=AC(ht, sample_lookup_ht, 'project_1'),
            AF=AF(ht, sample_lookup_ht, 'project_1'),
            AN=AN(ht, sample_lookup_ht, 'project_1'),
            hom=hom(ht, sample_lookup_ht, 'project_1'),
        )
        self.assertCountEqual(
            ht.collect(),
            [
                hl.Struct(id=0, AC=6, AF=0.5, AN=12, hom=2),
            ],
        )
