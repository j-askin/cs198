_base_ = [
    '../_base_/models/deeplabv3_r50-d8.py', '../_base_/datasets/lumenstone_dataset.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]
crop_size = (525, 700)
data_preprocessor = dict(size=crop_size)
model = dict(
    pretrained='open-mmlab://resnet101_v1c',
    backbone=dict(depth=101,
		  dilations=(1, 1, 1, 2),
		  strides=(1, 2, 2, 1)),
    data_preprocessor=data_preprocessor,
    decode_head=dict(type="ASPPHead",
		     dilations=(1 , 6, 12, 18),
		     num_classes=13),
    auxiliary_head=dict(num_classes=13))

# set path to dataset
data_root = 'data/lumenstone_augmented'
train_dataloader = dict(batch_size=4, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/train', seg_map_path='seg/train')))
val_dataloader = dict(batch_size=1, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
test_dataloader = val_dataloader