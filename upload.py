import requests
import os
import argparse
import logging


def upload_files(folder_path):
    url = "http://127.0.0.1:5000/upload"

    if not os.path.isdir(folder_path):
        logging.error(f"{folder_path} is not a valid directory.")
        return

    files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    if not files:
        logging.warning("No csv files found in the folder.")
        return

    for fname in files:
        fpath = os.path.join(folder_path, fname)
        with open(fpath, "r") as f:
            response = requests.post(url, files={"file": f})
            logging.info(f"Uploaded {fname}: {response.json()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload csv files from a folder.")
    parser.add_argument(
        "folder_path", type=str, help="Path to the folder containing csv files"
    )
    args = parser.parse_args()

    upload_files(args.folder_path)
