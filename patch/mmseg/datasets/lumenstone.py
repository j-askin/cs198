# Copyright (c) OpenMMLab. All rights reserved.
from mmseg.registry import DATASETS
from .basesegdataset import BaseSegDataset


@DATASETS.register_module()
class LumenstoneDataset(BaseSegDataset):
    METAINFO = dict(
        classes = (
            "Background", "Chalcopyrite", "Galena", "Magnetite",
            "Bornite", "Pyrrhotite","Pyrite/Marcasite", "Pentlandite",
            "Sphalerite", "Arsenopyrite", "Hematite","Tenantite-tetrahydrite",
            "Covelline",
        ),

        palette = [
            [0, 0, 0], [255, 0, 0], [203, 255, 0], [0, 255, 102],
            [0, 101, 255], [204, 0, 255], [255, 76, 76], [219, 255, 76],
            [76, 255, 147], [76, 147, 255], [219, 76, 255], [255, 153, 153],
            [234, 255, 153],
        ],
    )
    def __init__(self,
        img_suffix='.jpg',
        seg_map_suffix='.png',
        reduce_zero_label=True,
        **kwargs):
        super().__init__(
            img_suffix=img_suffix,
            seg_map_suffix=seg_map_suffix,
            reduce_zero_label=reduce_zero_label,
            **kwargs)
