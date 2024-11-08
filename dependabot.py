import os
from pathlib import Path
import yaml
import subprocess

dependabot_path = ".github/dependabot.yml"

dependency_files = [
    "pyproject.toml",
    "requirements.txt",
]


# Not used
def find_dependency_files(start_dir="."):
    found_files = []

    # Walk through the directory recursively
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            # If the file matches any dependency file name, add it to the list
            if file in dependency_files:
                found_files.append(os.path.join(root))

    return found_files


def format_with_prettier(file_path):
    config_path = str(Path(__file__).parent / ".prettierrc.yaml")
    subprocess.run(
        ["prettier", "--write", "--config", config_path, file_path], check=True
    )


def check_and_update_dependabot_file():
    if not os.path.exists(dependabot_path):
        return

    with open(dependabot_path, "r") as file:
        current_content = yaml.safe_load(file)

    updated = False
    for update in current_content.get("updates", []):
        if update.get("package-ecosystem") == "pip":
            updated = True
            update["schedule"] = {"interval": "weekly"}
            update["groups"] = {"python-updates": {"patterns": ["*"]}}

    if updated:
        with open(dependabot_path, "w") as file:
            yaml.dump(current_content, file, default_flow_style=False, sort_keys=False)
        format_with_prettier(dependabot_path)


if __name__ == "__main__":
    check_and_update_dependabot_file()
