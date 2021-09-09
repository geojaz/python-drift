# drifter README

This is a simple python script to detect drift in IAC repos/statefiles. 

For each run of the script, drifter will iterate over the list of statefiles listed in the 
drift_repos.txt. For each statefile listed in drift_repos.txt, if drift is detected, a slack 
notification will be sent to the channel configured via the Slack webhook.

![Screenshot](./assets/screenshot.png?raw=true)

## Usage

