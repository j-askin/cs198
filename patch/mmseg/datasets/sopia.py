# Copyright (c) OpenMMLab. All rights reserved.
from mmseg.registry import DATASETS
from .basesegdataset import BaseSegDataset


@DATASETS.register_module()
class SopiaDataset(BaseSegDataset):
    METAINFO = dict(
        classes = (
            "Background","Frothy Volcanic Glass", "Plagioclase", "Groundmass",
            "Silica", "Olivine", "Pyroxene", "Chlorite",
            "Epidote", "Opaque Minerals", "Amphibole", "Undefined",
            "Volcanic Glass", "Air Void", "Crack"
        ),

        palette = [
            [0, 0, 0], [31, 120, 180], [106, 61, 154], [33, 170, 157],
            [227, 26, 28], [255, 255, 153], [177, 89, 40], [85, 24, 183],
            [35, 60, 178], [16, 143, 155], [95, 13, 159], [255, 244, 116],
            [106, 176, 25], [168, 32, 34], [29, 13, 169]
        ],
    )
    def __init__(self,
            img_suffix='png',
            seg_map_suffix='png',
            reduce_zero_label=True,
            **kwargs):
        super().__init__(
            img_suffix=img_suffix,
            seg_map_suffix=seg_map_suffix,
            reduce_zero_label=reduce_zero_label,
            **kwargs)
