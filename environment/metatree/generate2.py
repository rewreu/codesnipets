import numpy as np
from datasets import Dataset, DatasetDict

def generate_synthetic_data(n_samples, n_features, n_classes, sequence_length=5):
    data = {}
    # Generate input_x: random floats with shape (sequence_length, n_features)
    data['input_x'] = [
        np.random.randn(sequence_length, n_features).astype(np.float32).tolist()
        for _ in range(n_samples)
    ]
    
    # Generate input_y: one-hot encoded labels
    labels = np.random.randint(0, n_classes, size=n_samples)
    data['input_y'] = [np.eye(n_classes, dtype=np.float32)[label].tolist() for label in labels]
    
    # Generate input_y_clean: same as input_y
    data['input_y_clean'] = data['input_y']
    
    # Generate status: random integers (e.g., 0 or 1), shape (sequence_length,)
    data['status'] = [
        np.random.randint(0, 2, size=sequence_length).astype(np.int64).tolist()
        for _ in range(n_samples)
    ]
    
    # Generate split_threshold: random floats, shape (sequence_length,)
    data['split_threshold'] = [
        np.random.rand(sequence_length).astype(np.float32).tolist()
        for _ in range(n_samples)
    ]
    
    # Generate split_dimension: integers between 0 and n_features - 1, shape (sequence_length,)
    data['split_dimension'] = [
        np.random.randint(0, n_features, size=sequence_length).astype(np.int64).tolist()
        for _ in range(n_samples)
    ]
    
    # Optional: Generate rtg for data filtering
    data['rtg'] = np.random.rand(n_samples).astype(np.float32).tolist()
    
    return data

# Parameters
n_train_samples = 1000
n_val_samples = 200
n_features = 16
n_classes = 10
sequence_length = 5  # Adjust this as needed

# Generate training data
train_data = generate_synthetic_data(n_train_samples, n_features, n_classes, sequence_length)

# Generate validation data
val_data = generate_synthetic_data(n_val_samples, n_features, n_classes, sequence_length)

# Create Dataset objects
train_dataset = Dataset.from_dict(train_data)
val_dataset = Dataset.from_dict(val_data)

# Create DatasetDict
dataset_dict = DatasetDict({
    'train': train_dataset,
    'validation': val_dataset
})

# Save the dataset to disk
dataset_dict.save_to_disk('synthetic_dataset')


"""
python generate_synthetic_data2.py

python run_train.py \
    --dataset_name synthetic_dataset \
    --load_from_local \
    --output_dir output_model \
    --n_feature 16 \
    --n_class 10 \
    --num_train_epochs 3 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 8 \
    --model_type llama \
    --num_heads 16 \
    --hidden_size 128 \
    --block_size 5

python metatree_pretrain.py \
    --dataset_name synthetic_dataset \
    --load_from_local \
    --output_dir output_model \
    --n_feature 16 \
    --n_class 10 \
    --num_train_epochs 3 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 8 \
    --model_type llama \
    --block_size 2048

"""
