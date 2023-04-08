# dataset settings
img_suffix='_raw.png',
seg_map_suffix='_seg.png',
reduce_zero_label=True,
dataset_type = 'SopiaDataset'
data_root = 'data/sopia/'
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
crop_size = (1200, 1920)

classes = (
    "Background",
    "Frothy Volcanic Glass",
    "Plagioclase",
    "Groundmass",
    "Silica",
    "Olivine",
    "Pyroxene",
    "Chlorite",
    "Epidote",
    "Opaque Minerals",
    "Amphibole",
    "Undefined",
    "Volcanic Glass",
    )

palette = [
    [0, 0, 0],
    [31, 120, 180],
    [106, 61, 154],
    [33, 170, 157],
    [227, 26, 28],
    [255, 255, 153],
    [177, 89, 40],
    [85, 24, 183],
    [35, 60, 178],
    [16, 143, 155],
    [95, 13, 159],
    [255, 244, 116],
    [106, 176, 25],
    ]


train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='Resize', img_scale=(1920, 1200), ratio_range=(0.5, 2.0)),
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
        img_scale=(1920, 1200),
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

