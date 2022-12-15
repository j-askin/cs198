# Copyright (c) OpenMMLab. All rights reserved.
from .builder import DATASETS
from .custom import CustomDataset


@DATASETS.register_module()
class SopiaDataset(CustomDataset):
    """COCO-Stuff dataset.

    In segmentation map annotation for COCO-Stuff, Train-IDs of the 10k version
    are from 1 to 171, where 0 is the ignore index, and Train-ID of COCO Stuff
    164k is from 0 to 170, where 255 is the ignore index. So, they are all 171
    semantic categories. ``reduce_zero_label`` is set to True and False for the
    10k and 164k versions, respectively. The ``img_suffix`` is fixed to '.jpg',
    and ``seg_map_suffix`` is fixed to '.png'.
    """
    CLASSES = (
        'Class 1', 'Class 2', 'Class 3', 'Class 4',
        'Class 5', 'Class 6', 'Class 7', 'Class 8',
        'Class 9', 'Class 10', 'Class 11', 'Class 12')

    PALETTE = [[0, 192, 64], [0, 64, 64], [0, 192, 96],
               [0, 0, 64], [0, 32, 192], [128, 128, 0],
               [64, 128, 32], [0, 32, 0], [0, 128, 0],
               [64, 0, 32], [0, 96, 128], [128, 128, 64]]

    def __init__(self, **kwargs):
        super(SopiaDataset, self).__init__(
            img_suffix='.png', seg_map_suffix='', **kwargs)
