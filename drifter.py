#!/usr/bin/env python

# Copyright 2021 Google LLC. This software is provided as is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.

"""
Script to detect drift in IAC(terraform) code and notify a slack channel

The main library used by this script is the slack_sdk library.
The slack_sdk library is used to send a message to Slack using a webhook url.

The script is designed to be run periodically as a cronjob.

usage: drifter.py [-h] [-f REPO_LIST]

It requires a single environment variable and the name of the file
containing the repo list.

SLACK_WEBHOOK_URL: the url for the Slack webhook.

positional arguments:
  cluster               The cluster to check for empty node pools

optional arguments:
  -h, --help            show this help message and exit
  -f REPO_LIST, --file REPO_LIST
                a text file with IAC repos/paths listed 1 per line, eg:
                    github.com:geojaz/drifter-test/repo-1
                    github.com:geojaz/drifter-test/repo-2
"""

import argparse
import os
import subprocess
import sys
import tempfile
from slack_sdk import WebhookClient

# Eric's test slack channel `export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/FAKE_DATA`

def check_repo(repo):
    """
    This is the main logic for this script and will be executed once for each repo scanned.
    If drift is detected in the repo (exit code == 2), fire a slack notification so someone
    can check on it.
    """
    cmd = f"git clone {get_git_source(repo)} {get_git_repo(repo)}"
    print (cmd)
    print ("Cloning IAC repo...")
    try:
        # Just in case the directory didn't get cleaned up last time
        subprocess.call(f"rm -rf {get_git_repo(repo)}", shell=True)
        subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError as git_error:
        sys.exit('error code: ', git_error.returncode, git_error.output)
    
    cmd = f"cd {get_git_repo(repo)}/{get_git_path(repo)} && terraform init && terraform plan -detailed-exitcode"
    print (cmd)
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as tf_error:
        if tf_error.returncode == 2:
            message = f"IAC repo {get_git_repo(repo)} is out of sync at path <{get_git_link(repo)}|{get_git_path(repo)}>"
            slack_message(message=message, webhook_url=get_slack_webhook().lstrip())

    cmd = f"rm -rf {get_git_repo(repo)}"
    try:
        subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError as tf_error:
        sys.exit('error code: ', tf_error.returncode, tf_error.output)


def slack_message(message, webhook_url):
    """
    Sends a message to Slack through a Webhook
    """
    webhook = WebhookClient(webhook_url)
    response = webhook.send(text=message)
    return response


def read_drift_list(file_path, file_name):
    """
    Helper function returns a list of IAC repos from a file
    """
    file = file_path + '/' + file_name
    if not os.path.isfile(file):
        return []
    with open(file) as f:
        return f.read().splitlines()


def get_git_source(repo):
    """
    Helper function to get the git source (for cloning) from drift_repos.txt
    """
    r = repo.split(':')[1]
    r = '/'.join([r.split('/')[0],r.split('/')[1]])
    return f"git@{get_git_server(repo)}:{r}.git"


def get_git_path(repo):
    """
    Helper function to get the path of IAC to check from drift_repos.txt format
    """
    r = repo.split(':')[1]
    return r.split('/')[2]


def get_git_repo(repo):
    """
    Helper function to get the git repo from the drift_repos.txt format
    """
    r = repo.split(':')[1]
    return r.split('/')[1]


def get_git_org(repo):
    """
    Helper function to get the git org from the drift_repos.txt format
    """
    return repo.split(':')[1].split('/')[0]


def get_git_server(repo):
    """
    Helper function to get the git server from the drift_repos.txt format
    """
    return repo.split(':')[0]

def get_git_link(repo):
    """
    Helper function to get direct link to IAC (used when drift is detected).
    """
    return f"https://{get_git_server(repo)}/{get_git_org(repo)}/{get_git_repo(repo)}/tree/master/{get_git_path(repo)}"


def get_slack_webhook():
    """
    Helper function to pick up slack webhook from envvar
    """
    return os.environ['SLACK_WEBHOOK_URL']


def main():
    parser = argparse.ArgumentParser(
        description=
        '''
        Script to detect drift in IAC(terraform) code and notify a slack channel
        It uses a single environment variable
        SLACK_WEBHOOK_URL: the url for the Slack webhook
        '''
    )
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        default="drift_repos.txt",
        help="a text file with IAC repos/paths listed 1 per line")
    args = parser.parse_args()
    repo_list = read_drift_list('.', args.file)
    for r in repo_list:
        check_repo(r)


if __name__ == "__main__":
    main()
