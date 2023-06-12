_base_ = [
    '../_base_/models/pspnet_r50-d8.py', '../_base_/datasets/lumenstone_dataset.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]
crop_size = (600, 800)
data_preprocessor = dict(size=crop_size)
model = dict(data_preprocessor=data_preprocessor,
	pretrained='open-mmlab://resnet101_v1c',
	backbone=dict(depth=101),
	decode_head=dict(num_classes=13),
	auxiliary_head=dict(num_classes=13))

# set path to dataset
data_root = 'data/lumenstone_augmented'
train_dataloader = dict(batch_size=2, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/train', seg_map_path='seg/train')))
val_dataloader = dict(batch_size=1, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
test_dataloader = val_dataloader
