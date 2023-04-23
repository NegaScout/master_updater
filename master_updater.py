#!/usr/bin/python3
from git import Repo
from os import path, kill
import signal
from configparser import ConfigParser

mu_config_file = '/opt/master_updater/config.ini'

config = ConfigParser(inline_comment_prefixes=("#",))
config.read(mu_config_file)

repo_path = config['MasterUpdater']['repo_path']
repo_url = config['MasterUpdater']['repo_url']
pid_file = config['MasterUpdater']['pid_file']
ssh_key = config['MasterUpdater']['ssh_key']

ssh_cmd = f'ssh -i {ssh_key} -o StrictHostKeyChecking=no'
repo = Repo(repo_path)
with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):

    if not path.exists(path.join(repo_path, '.git')):
        repo = Repo.clone_from(url=repo_url, to_path=repo_path)
    repo.git.checkout('main')
    for branch in repo.remote().fetch():
        if str(branch.remote_ref_path).strip() == 'main' and branch.flags == 64:
            repo.remote().pull()
            pid = None
            with open(pid_file, 'r') as pidfh:
                pid = int(pidfh.read())
                kill(pid, signal.SIGTERM)
            print(f"Updated repository and sent TERM to: { str(pid) }")
