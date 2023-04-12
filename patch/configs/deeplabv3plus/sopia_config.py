_base_ = [
    '../_base_/models/deeplabv3plus_r50-d8.py', '../_base_/datasets/sopia_dataset.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]
crop_size = (600, 600)
data_preprocessor = dict(size=crop_size)
model = dict(
    data_preprocessor=data_preprocessor,
    decode_head=dict(num_classes=13),
    auxiliary_head=dict(num_classes=13))
#uncomment to use augmented dataset
data_root = 'data/data/sopia'
train_dataloader = dict(
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
val_dataloader = dict(
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
test_dataloader = dict(
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
