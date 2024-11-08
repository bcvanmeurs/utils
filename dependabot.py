import os
from pathlib import Path
import yaml
import subprocess

dependabot_path = ".github/dependabot.yml"


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
