_base_ = [
    '../_base_/models/fastfcn_r50-d32_jpu_psp.py',
    '../_base_/datasets/sopia_dataset.py', '../_base_/default_runtime.py',
    '../_base_/schedules/schedule_80k.py'
]
crop_size = (600, 800)
data_preprocessor = dict(size=crop_size)
model = dict(data_preprocessor=data_preprocessor,
     decode_head=dict(num_classes=14),
     auxiliary_head=dict(num_classes=14))

# set path to dataset
data_root = 'data/sopia_xpl_augmented'
train_dataloader = dict(batch_size=4, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/train', seg_map_path='seg/train')))
val_dataloader = dict(batch_size=1, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
test_dataloader = val_dataloader
