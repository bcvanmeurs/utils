import requests
from tqdm import tqdm
from dotenv import dotenv_values
import datetime
import time

config = dotenv_values()

ORG_NAME = config["GITHUB_ORG"]
ORG_NO = config["GITHUB_ORG_NO"]
GITHUB_TOKEN = config["GITHUB_TOKEN"]

# GitHub API URL for the organization repos
org_repos_url = f"https://api.github.com/orgs/{ORG_NAME}/repos"

# Headers for authentication
headers = {"Authorization": f"token {GITHUB_TOKEN}"}


def make_request(url, params=None):
    response = requests.get(url, headers=headers, params=params)
    remaining_requests = int(response.headers.get("X-RateLimit-Remaining", 0))

    if remaining_requests == 0:
        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time()))
        sleep_time = max(0, reset_time - time.time() + 1)
        # print(response.headers)

        continue_time = datetime.datetime.fromtimestamp(reset_time + 1).strftime(
            "%H:%M:%S"
        )
        print(
            f"Rate limit exceeded. Sleeping for {int(sleep_time)} seconds till {continue_time}."
        )

        time.sleep(sleep_time)
        return make_request(url, params)  # Retry the request recursively

    return response


def get_repos():
    repos = []
    page = 1

    while True:
        response = make_request(org_repos_url, params={"page": page, "per_page": 100})
        repos_page = response.json()

        if not repos_page:
            break

        for repo in repos_page:
            if not repo["archived"]:
                repos.append(repo["name"])

        page += 1

    return repos


def get_python_repos():
    python_repos = []
    repos = get_repos()

    for repo in tqdm(repos, desc="Processing Repos"):
        repo_language_url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/languages"
        language_response = make_request(repo_language_url)
        languages = language_response.json()

        if (
            "Python" in languages
            # and languages["Python"] > sum(languages.values()) * 0.5
        ):
            python_repos.append(repo)

    python_repos.sort(key=str.lower)
    return python_repos


def print_yaml(repos: list[str]):
    print("repo:")
    for repo in repos:
        print(f"  - adarga-ltd/{repo}")


if __name__ == "__main__":
    repos = get_python_repos()
    print_yaml(repos)
