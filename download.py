import requests
import os
import argparse
import db
import logging


def download_plots(folder, usernames=None):
    url_template = "http://127.0.0.1:5000/visualize?username={}"

    if not os.path.exists(folder):
        os.makedirs(folder)

    # Not so nice query there in the script.
    with db.connection() as con:
        with con.cursor() as cur:
            cur.execute("SELECT username from Users")
            usernames = cur.fetchall()

    for username in usernames:
        username = username[0]
        url = url_template.format(username)
        response = requests.get(url)

        if response.status_code == 200:
            file_path = os.path.join(folder, f"{username}.png")
            with open(file_path, "wb") as f:
                f.write(response.content)
            logging.info(f"Downloaded plot for {username}: {file_path}")
        else:
            logging.error(
                f"Failed to download plot for {username}: {response.status_code}, {response.text}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download plots for users.")
    parser.add_argument("folder_path", type=str, help="Path to save downloaded plots")
    args = parser.parse_args()

    download_plots(args.folder_path)
