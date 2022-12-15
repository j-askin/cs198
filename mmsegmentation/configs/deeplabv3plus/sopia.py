_base_ = [
    '../_base_/models/deeplabv3plus_r50-d8.py',
    '../_base_/datasets/sopia.py',
    '../_base_/default_runtime.py',
    '../_base_/schedules/schedule_160k.py'
]
model = dict(
    decode_head=dict(num_classes=16),
    auxiliary_head=dict(num_classes=16),
    pretrained='open-mmlab://resnet101_v1c',
    backbone=dict(depth=101))
