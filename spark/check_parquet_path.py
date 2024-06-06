import os
import s3fs

def check_parquet_path(path):
    """
    Checks if the _SUCCESS file is present in a Parquet path and if the folder contains more than one file.

    Args:
        path (str): The path to the Parquet directory. This can be a local path or an S3 path.

    Returns:
        dict: A dictionary with two keys:
            - 'success_file': A boolean indicating if the _SUCCESS file is present.
            - 'file_count': An integer indicating the number of files in the directory.
    """
    if path.startswith("s3://"):
        fs = s3fs.S3FileSystem()
    else:
        fs = None

    # Check for _SUCCESS file
    success_file = False
    file_count = 0

    if fs:
        # S3 path
        files = fs.ls(path)
        for file in files:
            if file.endswith("_SUCCESS"):
                success_file = True
            if not file.endswith("/"):  # Count files, ignore directories
                file_count += 1
    else:
        # Local path
        for root, dirs, files in os.walk(path):
            for file in files:
                if file == "_SUCCESS":
                    success_file = True
                file_count += 1

    # Prepare result
    result = {
        "success_file": success_file,
        "file_count": file_count
    }
    return result

# Example usage:
# For S3 path:
s3_path = "s3://your-bucket/path/to/parquet/"
result_s3 = check_parquet_path(s3_path)
print(result_s3)

# For local path:
local_path = "/path/to/parquet/"
result_local = check_parquet_path(local_path)
print(result_local)
