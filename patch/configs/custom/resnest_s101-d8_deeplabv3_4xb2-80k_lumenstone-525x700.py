_base_ = ['../_base_/models/deeplabv3_r50-d8.py', '../_base_/datasets/lumenstone_dataset.py',
	  '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py']
crop_size = (525, 700)
data_preprocessor = dict(size=crop_size)
model = dict(
    pretrained='open-mmlab://resnest101',
    data_preprocessor=data_preprocessor,
    backbone=dict(
        type='ResNeSt',
	depth=101,
        stem_channels=128,
        radix=2,
        reduction_factor=4,
        avg_down_stride=True),
    decode_head=dict(num_classes=13),
    auxiliary_head=dict(num_classes=13)
)

# set path to dataset
data_root = 'data/lumenstone_augmented'
train_dataloader = dict(batch_size=2, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/train', seg_map_path='seg/train')))
val_dataloader = dict(batch_size=1, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
test_dataloader = val_dataloader
