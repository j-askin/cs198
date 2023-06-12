# dataset settings
dataset_type = 'SopiaDataset'
data_root = 'data/sopia_augmented'
crop_size = (600, 800)
# METAINFO = dict(
#         classes = (
#             "Background", "Frothy Volcanic Glass", "Plagioclase", "Groundmass",
#             "Silica", "Olivine", "Pyroxene", "Chlorite",
#             "Epidote", "Opaque Minerals", "Amphibole", "Undefined",
#             "Volcanic Glass", "Air Void", "Crack"
#         ),
#         palette = [
#             [0, 0, 0], [31, 120, 180], [106, 61, 154], [33, 170, 157],
#             [227, 26, 28], [255, 255, 153], [177, 89, 40], [85, 24, 183],
#             [35, 60, 178], [16, 143, 155], [95, 13, 159], [255, 244, 116],
#             [106, 176, 25], [168, 32, 34], [29, 13, 169],
#         ],
#     )
# img_suffix='png',
# seg_map_suffix='png',
# reduce_zero_label=False
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', reduce_zero_label=True),
    dict(
        type='RandomResize',
        scale=(800, 600),
        ratio_range=(0.5, 2.0),
        keep_ratio=True),
    dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
    dict(type='RandomFlip', prob=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(type='PackSegInputs', meta_keys=dict(pad_shape=crop_size))
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='Resize', scale=(800, 600), keep_ratio=True),
    dict(type='LoadAnnotations', reduce_zero_label=True),
    dict(type='PackSegInputs', meta_keys=dict(
                                              pad_shape=crop_size,
                                              ori_shape=(1200, 1920, 3),
                                              img_shape=crop_size
                                             ))
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
            ], [dict(type='LoadAnnotations')], [dict(type='PackSegInputs', meta_keys=dict(pad_shape=crop_size))]
        ])
]
train_dataloader = dict(
    batch_size=2,
    num_workers=2,
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
