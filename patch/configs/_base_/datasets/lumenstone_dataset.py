# dataset settings
img_suffix='.jpg',
seg_map_suffix='.png',
reduce_zero_label=True,
dataset_type = 'LumenstoneDataset'
data_root = 'data/lumenstone/'
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
crop_size = (900, 1200)

classes = (
    "Background",
    "Chalcopyrite",
    "Galena",
    "Magnetite",
    "Bornite",
    "Pyrrhotite",
    "Pyrite/Marcasite",
    "Pentlandite",
    "Sphalerite",
    "Arsenopyrite",
    "Hematite",
    "Tenantite-tetrahydrite",
    "Covelline",
    )

palette = [
    [0, 0, 0],
    [255, 0, 0],
    [203, 255, 0],
    [0, 255, 102],
    [0, 101, 255],
    [204, 0, 255],
    [255, 76, 76],
    [219, 255, 76],
    [76, 255, 147],
    [76, 147, 255],
    [219, 76, 255],
    [255, 153, 153],
    [234, 255, 153],
    ]


train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', reduce_zero_label=True),
    dict(type='Resize', img_scale=(1200, 900), ratio_range=(0.5, 2.0)),
    dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
    dict(type='RandomFlip', prob=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size=crop_size, pad_val=0, seg_pad_val=255),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(1200, 900),
        # img_ratios=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75],
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
data = dict(
    samples_per_gpu=2,
    workers_per_gpu=2,
    train=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='raw/train',
        ann_dir='seg/train',
        pipeline=train_pipeline),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='raw/val',
        ann_dir='seg/val',
        pipeline=test_pipeline),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='raw/val',
        ann_dir='seg/val',
        pipeline=test_pipeline))

