import hmac
from typing import Optional
from fastapi import FastAPI, Request
from .config import get_config
import logging
import os
import subprocess
import uvicorn
from shellescape import quote

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def command_preparation(command, user):
    if user is None:
        return command

    return ["su", user, "-s", "/bin/bash", "-c", " ".join([quote(c) for c in command])]


@app.post(path="/pull/{repo}")
async def pull(request: Request, repo: str):
    c = get_config()

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
        subprocess.run(command_preparation(["git", "reset", "--hard"], repo_config.get("executing_user")))

    pull_process = subprocess.run(command_preparation(["git", "pull"], repo_config.get("executing_user")))

    git_url_process = subprocess.run(command_preparation(
        ["git", "config", "--get", "remote.origin.url"], repo_config.get("executing_user")), capture_output=True
    )
    git_url = git_url_process.stdout.decode("UTF-8").split("\n")[0]

    latest_git_log_process = subprocess.run(command_preparation(["git", "log", "-1", "--pretty=%B"]), capture_output=True)
    subprocess.run(command_preparation(["wall", "Puller hat gepullt ({})".format(latest_git_log_process.stdout)]))

    os.chdir(path)

    if pull_process.returncode != 0 and repo_config.get("git_delete_if_pull_failed"):
        subprocess.run(command_preparation(["rm", "-rf", repo_config["path"]], repo_config.get("executing_user")))
        subprocess.run(command_preparation(["git", "clone", git_url, repo_config["path"]], repo_config.get("executing_user")))
        pass


    return {}

def start_server():
    try:
        port = int(os.environ['PULLER_PORT'])
    except:
        port = 8000

    uvicorn.run("puller:app", host="0.0.0.0", port=port, log_level="info")
