# dataset settings
dataset_type = 'LumenstoneDataset'
data_root = 'data/lumenstone/'
crop_size = (900, 1200)
#metainfo = dict(
#    classes = (
#        "Background", "Chalcopyrite", "Galena", "Magnetite",
#        "Bornite", "Pyrrhotite","Pyrite/Marcasite", "Pentlandite",
#        "Sphalerite", "Arsenopyrite", "Hematite","Tenantite-tetrahydrite",
#        "Covelline",
#    ),
#    palette = [
#        [0, 0, 0], [255, 0, 0], [203, 255, 0], [0, 255, 102],
#        [0, 101, 255], [204, 0, 255], [255, 76, 76], [219, 255, 76],
#        [76, 255, 147], [76, 147, 255], [219, 76, 255], [255, 153, 153],
#        [234, 255, 153],
#    ],
#)
#img_suffix='.jpg',
#seg_map_suffix='.png',
#ignore_index=0,
#reduce_zero_label=True,
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', reduce_zero_label=True),
    dict(
        type='RandomResize',
        scale=(1200, 900),
        ratio_range=(0.5, 2.0),
        keep_ratio=True),
    dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
    dict(type='RandomFlip', prob=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(type='PackSegInputs')
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='Resize', scale=(1200, 900), keep_ratio=True),
    dict(type='LoadAnnotations', reduce_zero_label=True),
    dict(type='PackSegInputs')
]
img_ratios = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75]
tta_pipeline = [
    dict(type='LoadImageFromFile', backend_args=None),
    dict(
        type='TestTimeAug',
        transforms=[
            [
                dict(type='Resize', scale_factor=r, keep_ratio=True)
                for r in img_ratios
            ],
            [
                dict(type='RandomFlip', prob=0., direction='horizontal'),
                dict(type='RandomFlip', prob=1., direction='horizontal')
            ], [dict(type='LoadAnnotations')], [dict(type='PackSegInputs')]
        ])
]
train_dataloader = dict(
    batch_size=4,
    num_workers=4,
    persistent_workers=True,
    sampler=dict(type='InfiniteSampler', shuffle=True),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        reduce_zero_label=True,
        data_prefix=dict(
            img_path='raw/train', seg_map_path='seg/train'),
        pipeline=train_pipeline))
val_dataloader = dict(
    batch_size=1, #must be set to 1
    num_workers=4,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        reduce_zero_label=True,
        data_prefix=dict(
            img_path='raw/val', seg_map_path='seg/val'),
        pipeline=test_pipeline))
test_dataloader = val_dataloader

val_evaluator = dict(type='IoUMetric', iou_metrics=['mIoU'])
test_evaluator = val_evaluator