_base_ = [
    '../_base_/models/sopia_model.py', '../_base_/datasets/sopia_dataset.py',
    '../_base_/sopia_runtime.py', '../_base_/schedules/sopia_schedule.py'
]
model = dict(
    decode_head=dict(num_classes=13),
    auxiliary_head=dict(num_classes=13))