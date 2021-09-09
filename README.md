# drifter README

This is a simple python script to detect drift in IAC repos/statefiles. 

For each run of the script, drifter will iterate over the list of statefiles listed in the REPO_LIST config file. For each statefile listed, if drift is detected, a slack notification will be sent to the channel configured via the Slack webhook. The notification provides a direct link to the offending statefile.

![Screenshot](./assets/screenshot.png?raw=true)


## Configuration and Secrets

Typically this would be run in some sort of cron automation, perhaps as a GitLab or Kubernetes 
cron job. Regardles of where the job runs, there are a few elements of config to consider, some which are secrets.

### SLACK_WEBHOOK_URL

This should be configured in Slack and then injected as an envvar to the process:
`export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/FAKE_DATA`

### REPO_LIST

This is the list of repos that the drifter needs to iterate over. drifter can select the repo-list file with the `-f` flag.
Since it is possible for multiple terraform states to be present in a single IAC repo, the format of the repo-list file requires a single line per repo-state combination in the following format:

`github.com:geojaz/drifter-test/repo-1`

Git Server: github.com
Owner/group: geojaz
Repo name: drifter-test
Repo path/statefile path: repo-1

**Important!** The actor executing drifter (whether a service account or a human) needs read only access to all of the git repos listed in the repo-list config file. 

It also needs read only GCP org access. This code should work the same for AWS or other terraform managed clouds, but will similarly need broad read-only access sufficient to run `terraform plan`. 

The implementation here is left to the user since there are several options that vary depending on use case. In automation for GCP, the recommendation is to use Workload Identity to act as a service account with the correct permissions. Alternatively, `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key`.



