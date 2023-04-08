# Copyright (c) OpenMMLab. All rights reserved.
import os.path as osp

import mmcv
import numpy as np
from PIL import Image

from .builder import DATASETS
from .custom import CustomDataset


@DATASETS.register_module()
class LumenstoneDataset(CustomDataset):
    CLASSES = ("Background", "Chalcopyrite", "Galena", "Magnetite", "Bornite", "Pyrrhotite",
               "Pyrite/Marcasite", "Pentlandite", "Sphalerite", "Arsenopyrite", "Hematite", 
               "Tenantite-tetrahydrite", "Covelline")

    PALETTE = [[0, 0, 0], [255, 0, 0], [203, 255, 0], [0, 255, 102], [0, 101, 255],
               [204, 0, 255], [255, 76, 76], [219, 255, 76], [76, 255, 147],
               [76, 147, 255], [219, 76, 255], [255, 153, 153], [234, 255, 153]]

    def __init__(self, **kwargs):
        super(LumenstoneDataset, self).__init__(
            img_suffix='.jpg',
            seg_map_suffix='.png',
            reduce_zero_label=True,
            **kwargs)

    def results2img(self, results, imgfile_prefix, to_label_id, indices=None):
        if indices is None:
            indices = list(range(len(self)))
        mmcv.mkdir_or_exist(imgfile_prefix)
        result_files = []
        for result, idx in zip(results, indices):
            filename = self.img_infos[idx]['filename']
            basename = osp.splitext(osp.basename(filename))[0]
            png_filename = osp.join(imgfile_prefix, f'{basename}.png')
            result = result + 1
            output = Image.fromarray(result.astype(np.uint8))
            output.save(png_filename)
            result_files.append(png_filename)
        return result_files

    def format_results(self,
                       results,
                       imgfile_prefix,
                       to_label_id=True,
                       indices=None):
        if indices is None:
            indices = list(range(len(self)))
        assert isinstance(results, list), 'results must be a list.'
        assert isinstance(indices, list), 'indices must be a list.'
        result_files = self.results2img(results, imgfile_prefix, to_label_id, indices)
        return result_files
