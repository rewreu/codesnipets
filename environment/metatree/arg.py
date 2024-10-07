import argparse
import yaml

def parse_args():
    # Step 1: Create a basic parser to check for the presence of a config file
    config_parser = argparse.ArgumentParser(description="Finetune a transformers model")
    config_parser.add_argument("--config", type=str, default=None, help="Path to the config file.")
    config_args, remaining_args = config_parser.parse_known_args()

    # Step 2: If config file is provided, load arguments from YAML
    if config_args.config:
        with open(config_args.config, "r") as file:
            config = yaml.safe_load(file)
        
        # Flatten the YAML file structure (optional, adjust as needed)
        flattened_args = {**config.get("dataset", {}), **config.get("model", {}), **config.get("training", {}), 
                          **config.get("optimization", {}), **config.get("advanced_options", {})}
        return argparse.Namespace(**flattened_args)

    # Step 3: If no config file, define the full command-line arguments parser as before
    parser = argparse.ArgumentParser(description="Finetune a transformers model on a causal language modeling task")

    # Dataset arguments
    parser.add_argument("--dataset_name", type=str, default=None, help="The name of the dataset to use.")
    parser.add_argument("--dataset_config_name", type=str, default=None, help="The configuration name of the dataset.")
    parser.add_argument("--train_file", type=str, default=None, help="A csv or json file containing the training data.")
    parser.add_argument("--validation_file", type=str, default=None, help="A csv or json file containing validation data.")
    parser.add_argument("--validation_split_percentage", type=int, default=5, help="Percentage of the train set for validation.")
    
    # Model arguments
    parser.add_argument("--model_name_or_path", type=str, default=None, help="Path to pretrained model or model identifier.")
    parser.add_argument("--config_name", type=str, default=None, help="Pretrained config name or path if not the same as model_name.")
    parser.add_argument("--tokenizer_name", type=str, default=None, help="Pretrained tokenizer name or path if not the same as model_name.")
    parser.add_argument("--use_slow_tokenizer", action="store_true", help="Use a slow tokenizer (not backed by 🤗 Tokenizers library).")
    
    # Training arguments
    parser.add_argument("--per_device_train_batch_size", type=int, default=8, help="Batch size for training.")
    parser.add_argument("--per_device_eval_batch_size", type=int, default=8, help="Batch size for evaluation.")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Initial learning rate.")
    parser.add_argument("--weight_decay", type=float, default=0.0, help="Weight decay to use.")
    parser.add_argument("--num_train_epochs", type=int, default=3, help="Total number of training epochs.")
    parser.add_argument("--max_train_steps", type=int, default=None, help="Total number of training steps to perform.")
    parser.add_argument("--max_eval_steps", type=int, default=None, help="Total number of evaluation steps.")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1, help="Number of steps to accumulate before backpropagation.")
    
    # Advanced training arguments
    parser.add_argument("--lr_scheduler_type", type=str, choices=["linear", "cosine", "constant"], default="linear", help="Scheduler type.")
    parser.add_argument("--num_warmup_steps", type=int, default=0, help="Number of warmup steps.")
    parser.add_argument("--output_dir", type=str, default=None, help="Output directory for model.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    
    # Additional arguments can go here as needed...

    # Step 4: Parse command-line arguments if no config file is specified
    return parser.parse_args(remaining_args)


# Example usage:
if __name__ == "__main__":
    args = parse_args()
    print(args)
