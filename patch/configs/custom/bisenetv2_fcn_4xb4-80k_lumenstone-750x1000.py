_base_ = [
    '../_base_/models/bisenetv2.py',
    '../_base_/datasets/lumenstone_dataset.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]
crop_size = (750, 1000)
data_preprocessor = dict(size=crop_size)
model = dict(data_preprocessor=data_preprocessor)
param_scheduler = [
    dict(type='LinearLR', by_epoch=False, start_factor=0.1, begin=0, end=1000),
    dict(
        type='PolyLR',
        eta_min=1e-4,
        power=0.9,
        begin=1000,
        end=160000,
        by_epoch=False,
    )
]
optimizer = dict(type='SGD', lr=0.05, momentum=0.9, weight_decay=0.0005)
optim_wrapper = dict(type='OptimWrapper', optimizer=optimizer)

# set path to dataset
data_root = 'data/lumenstone_augmented'
train_dataloader = dict(batch_size=4, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/train', seg_map_path='seg/train')))
val_dataloader = dict(batch_size=1, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
test_dataloader = val_dataloader
