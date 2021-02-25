import hmac
from typing import Optional
from fastapi import FastAPI, Request
import config
import logging
import os
import subprocess

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post(path="/pull/{repo}")
async def pull(request: Request, repo: str):
    c = config.get_config()

    try:
        repo_config = c[repo]
    except KeyError:
        logger.error("Repo does not seem to be configured")
        return

    body = await request.body()

    signature_local = hmac.new(
        bytes(repo_config["shared_secret"], "UTF-8"), body, digestmod="SHA256"
    ).hexdigest()
    signature_request = request.headers["X-Hub-Signature"].split("=")[1]

    if signature_local != signature_request:
        logger.error("Repo does not seem to be configured")
        return

    path = os.getcwd()

    os.chdir(repo_config["path"])

    if repo_config.get("git_reset"):
        logging.info("Resetting the repository before pulling")
        subprocess.run(["git", "reset", "--hard"])

    pull_process = subprocess.run(["git", "pull"])

    git_url_process = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"], capture_output=True
    )
    git_url = git_url_process.stdout.decode("UTF-8").split("\n")[0]
    logging.info(f"Captured origin: {git_url}")
    os.chdir(path)

    if pull_process.returncode != 0 and repo_config.get("git_delete_if_pull_failed"):
        subprocess.run(["rm", "-rf", repo_config["path"]])
        subprocess.run(["git", "clone", git_url, repo_config["path"]])
        pass

    return {}