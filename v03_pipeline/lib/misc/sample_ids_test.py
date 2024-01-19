import unittest

import hail as hl

from v03_pipeline.lib.misc.sample_ids import (
    MatrixTableSampleSetError,
    remap_sample_ids,
    subset_samples,
)

CALLSET_MT = hl.MatrixTable.from_parts(
    rows={'variants': [1, 2]},
    cols={'s': ['HG00731', 'HG00732', 'HG00733']},
    entries={
        'HL': [
            [0.0, hl.missing(hl.tfloat), 0.3],
            [0.1, 0.2, 0.3],
        ],
    },
).key_cols_by('s')


class SampleLookupTest(unittest.TestCase):
    def test_remap_2_sample_ids(self) -> None:
        # remap 2 of 3 samples in callset
        project_remap_ht = hl.Table.parallelize(
            [
                {'s': 'HG00731', 'seqr_id': 'HG00731_1'},
                {'s': 'HG00732', 'seqr_id': 'HG00732_1'},
            ],
            hl.tstruct(
                s=hl.tstr,
                seqr_id=hl.tstr,
            ),
            key='s',
        )

        remapped_mt = remap_sample_ids(
            CALLSET_MT,
            project_remap_ht,
            ignore_missing_samples_when_remapping=True,
        )

        self.assertEqual(remapped_mt.cols().count(), 3)
        self.assertEqual(
            remapped_mt.cols().collect(),
            [
                hl.Struct(
                    col_idx=0,
                    s='HG00731_1',
                    seqr_id='HG00731_1',
                    vcf_id='HG00731',
                ),
                hl.Struct(
                    col_idx=1,
                    s='HG00732_1',
                    seqr_id='HG00732_1',
                    vcf_id='HG00732',
                ),
                hl.Struct(col_idx=2, s='HG00733', seqr_id='HG00733', vcf_id='HG00733'),
            ],
        )

    def test_remap_sample_ids_remap_has_duplicate(self) -> None:
        # remap file has 2 rows for HG00732
        project_remap_ht = hl.Table.parallelize(
            [
                {'s': 'HG00731', 'seqr_id': 'HG00731_1'},
                {'s': 'HG00732', 'seqr_id': 'HG00732_1'},
                {'s': 'HG00732', 'seqr_id': 'HG00732_1'},  # duplicate
            ],
            hl.tstruct(
                s=hl.tstr,
                seqr_id=hl.tstr,
            ),
            key='s',
        )

        with self.assertRaises(ValueError):
            remap_sample_ids(
                CALLSET_MT,
                project_remap_ht,
                ignore_missing_samples_when_remapping=True,
            )

    def test_remap_sample_ids_remap_has_missing_samples(self) -> None:
        # remap file has 4 rows, but only 3 samples in callset
        project_remap_ht = hl.Table.parallelize(
            [
                {'s': 'HG00731', 'seqr_id': 'HG00731_1'},
                {'s': 'HG00732', 'seqr_id': 'HG00732_1'},
                {'s': 'HG00733', 'seqr_id': 'HG00733_1'},
                {'s': 'HG00734', 'seqr_id': 'HG00734_1'},  # missing in callset
            ],
            hl.tstruct(
                s=hl.tstr,
                seqr_id=hl.tstr,
            ),
            key='s',
        )

        with self.assertRaises(MatrixTableSampleSetError):
            remap_sample_ids(
                CALLSET_MT,
                project_remap_ht,
                ignore_missing_samples_when_remapping=False,
            )

    def test_subset_samples(self):
        # subset 2 of 3 samples in callset
        sample_subset_ht = hl.Table.parallelize(
            [
                {'s': 'HG00731'},
                {'s': 'HG00732'},
            ],
            hl.tstruct(s=hl.tstr),
            key='s',
        )

        subset_mt = subset_samples(
            CALLSET_MT,
            sample_subset_ht,
            ignore_missing_samples_when_subsetting=True,
        )

        self.assertEqual(subset_mt.cols().count(), 2)
        self.assertEqual(
            subset_mt.cols().collect(),
            [
                hl.Struct(col_idx=0, s='HG00731'),
                hl.Struct(col_idx=1, s='HG00732'),
            ],
        )

    def test_subset_samples_zero_samples(self):
        # subset 0 of 3 samples in callset
        sample_subset_ht = hl.Table.parallelize(
            [],
            hl.tstruct(s=hl.tstr),
            key='s',
        )

        with self.assertRaises(MatrixTableSampleSetError):
            subset_samples(
                CALLSET_MT,
                sample_subset_ht,
                ignore_missing_samples_when_subsetting=True,
            )

    def test_subset_samples_missing_samples(self):
        # subset 2 of 3 samples in callset, but 1 is missing
        sample_subset_ht = hl.Table.parallelize(
            [
                {'s': 'HG00731'},
                {'s': 'HG00732'},
                {'s': 'HG00734'},  # missing in callset
            ],
            hl.tstruct(s=hl.tstr),
            key='s',
        )

        with self.assertRaises(MatrixTableSampleSetError):
            subset_samples(
                CALLSET_MT,
                sample_subset_ht,
                ignore_missing_samples_when_subsetting=False,
            )
