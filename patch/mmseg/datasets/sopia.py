# Copyright (c) OpenMMLab. All rights reserved.
import os.path as osp

import mmcv
import numpy as np
from PIL import Image

from .builder import DATASETS
from .custom import CustomDataset


@DATASETS.register_module()
class SopiaDataset(CustomDataset):
    CLASSES = ("Background", "Frothy Volcanic Glass", "Plagioclase", "Groundmass", "Silica", "Olivine",
               "Pyroxene", "Chlorite", "Epidote", "Opaque Minerals", "Amphibole", "Undefined",
               "Volcanic Glass")

    PALETTE = [[0, 0, 0], [31, 120, 180], [106, 61, 154], [33, 170, 157], [227, 26, 28],
               [255, 255, 153], [177, 89, 40], [85, 24, 183], [35, 60, 178],
               [16, 143, 155], [95, 13, 159], [255, 244, 116], [106, 176, 25]]

    def __init__(self, **kwargs):
        super(SopiaDataset, self).__init__(
            img_suffix='_raw.png',
            seg_map_suffix='_seg.png',
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
