# Copyright (c) OpenMMLab. All rights reserved.
from mmseg.registry import DATASETS
from .basesegdataset import BaseSegDataset


@DATASETS.register_module()
class SopiaDataset(BaseSegDataset):
    METAINFO = dict(
        classes = (
            "Background", "Frothy Volcanic Glass", "Plagioclase", "Groundmass",
            "Silica", "Olivine", "Pyroxene", "Chlorite", 
            "Epidote", "Opaque Minerals", "Amphibole", "Undefined",
            "Volcanic Glass",
        ),

        palette = [
            [0, 0, 0], [31, 120, 180], [106, 61, 154], [33, 170, 157],
            [227, 26, 28], [255, 255, 153], [177, 89, 40], [85, 24, 183],
            [35, 60, 178], [16, 143, 155], [95, 13, 159], [255, 244, 116],
            [106, 176, 25],
        ],
    )
    def __init__(self, **kwargs):
        super(SopiaDataset, self).__init__(
            img_suffix='_raw.png',
            seg_map_suffix='_seg.png',
            reduce_zero_label=True,
            **kwargs)