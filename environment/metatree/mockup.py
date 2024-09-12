import pandas as pd
import numpy as np

# Creating a fake dataset with the required columns
data = {
    'input_x': np.random.rand(100, 10).tolist(),  # 100 rows of 10 features
    'input_y': np.random.randint(0, 2, size=(100,)).tolist(),  # Binary classification
    'input_y_clean': np.random.randint(0, 2, size=(100,)).tolist(),  # Another binary column
    'status': np.random.choice([0, 1], size=100).tolist(),  # Status column, binary values
    'split_threshold': np.random.rand(100).tolist(),  # Continuous values for threshold
    'split_dimension': np.random.randint(0, 5, size=(100,)).tolist()  # Categorical split dimension
}

# Convert the dictionary to a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame as CSV
df.to_csv('fake_dataset.csv', index=False)


# python run_train.py --train_file fake_dataset.csv --validation_file fake_dataset.csv --model_type llama --block_size 20 --checkpointing_steps 100 --resume_from_checkpoint false --num_heads 16
