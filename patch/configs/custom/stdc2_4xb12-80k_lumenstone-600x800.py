_base_ = './lumenstone_config.py'
model = dict(backbone=dict(backbone_cfg=dict(stdc_type='STDCNet2')))
# set path to dataset
data_root = 'data/lumenstone_augmented'
train_dataloader = dict(batch_size=12, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/train', seg_map_path='seg/train')))
val_dataloader = dict(batch_size=1, num_workers=4,
    dataset=dict(data_root=data_root,
        data_prefix=dict(img_path='raw/val', seg_map_path='seg/val')))
test_dataloader = val_dataloader