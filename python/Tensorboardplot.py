import os
import pandas as pd
import matplotlib.pyplot as plt
from tensorboard.backend.event_processing import event_accumulator

def compare_experiments(list_exp, metric):
    """
    Compare a specific scalar metric across multiple TensorBoard experiment folders.
    
    Args:
        list_exp (list): List of experiment folder paths (each containing TensorBoard logs).
        metric (str): The name of the scalar metric to compare (e.g., "loss", "accuracy").
    """
    plt.figure(figsize=(10, 6))
    
    for exp_path in list_exp:
        # Find the first .tfevents file in the experiment folder
        event_file = None
        for file in os.listdir(exp_path):
            if file.startswith("events.out.tfevents"):
                event_file = os.path.join(exp_path, file)
                break
        
        if not event_file:
            print(f"No event file found in {exp_path}, skipping.")
            continue

        # Load and extract metric
        ea = event_accumulator.EventAccumulator(event_file)
        ea.Reload()
        
        if metric not in ea.Tags().get("scalars", []):
            print(f"Metric '{metric}' not found in {exp_path}, skipping.")
            continue

        data = pd.DataFrame(ea.Scalars(metric))
        label = os.path.basename(exp_path)
        plt.plot(data["step"], data["value"], label=label)

    plt.xlabel("Step")
    plt.ylabel(metric)
    plt.title(f"Comparison of '{metric}' across experiments")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
