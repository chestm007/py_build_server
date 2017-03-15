[![Code Climate](https://codeclimate.com/github/chestm007/py_build_server/badges/gpa.svg)](https://codeclimate.com/github/chestm007/py_build_server)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)


An automated build server written for Python (but should work with most other languages), runs under python2 or python3

#### About
Monitors git repository either by polling or listening for webhook messages, and when new tagged versions are released, 
builds and uploads to your chosen repository via twine.

- Features
  - Bitbucket and Github webhook support
  - Has a super cool API (not really, only 3 payloads are supported)
  - Can run tests before building and uploading (nosetest only at the moment.)

#### Installation
`sudo pip2 install py-build-server`

You will need to modify `config.yaml` file in `/etc/py-build-server/` to match your deployment:

```yaml
# this file belongs in /etc/py-build-server/config/yaml
#
# Demo entry using all possible config options: O denotes optionals
####
#
### this section defines how to start the API server
### api and repository_update_method cannot bind to the same address, port and subdomain
#
# api:
#     listen_address: 127.0.0.1         # listen on this address
#     strict_port_checking: true        # (O) setting to false may let the api accept requests intended
#                                       #     for another module
#     port: 9832                        # port to listen on
#     subdomain: /api                   # subdomain to bind to
#
### this section defines how to check for changes
#
# repository_update_method: polling     # (O) poll git repo
# repository_update_method:             # (O) --alternatively--
#     github_webhook:                   # (O) specify webhook to recieve notifications from github
#         subdomain: /github            # listen to this subdomain (http://<your_url/)
#         listen_address: 192.168.1.2   # listen on this address
#         port: 8080                    # listen on this port
#     bitbucket_webhook:                # (O) specify webhook to recieve notifications from github
#         subdomain: /bitbucket         # listen to this subdomain (http://<your_url/)
#         listen_address: 192.168.1.2   # listen on this address
#         port: 8090                    # listen on this port
#
### this section set logging options
#
# logging:                              # (O)
#     level: debug                      # (O) DEBUG|WARN|INFO|ERROR|OFF (case doesnt matter)
#
### this section sets repository specific settings
#
# repositories:
#     py_build_server:                  # repository name, as seen by remote
#         dir: /home/max/git/py_build_server
#         update_method: github_webhook # (O) bitbucket_webhook|github_webhook|polling (default: polling)
#         interval: 10                  # (O) minutes between repo checks (only needed if polling)
#         remote: origin                # (O) remote name to fetch (default: origin)
#         tests:                        # (O) if set, run all tests listed here
#             - command: cd {repository_dir}; nosetests -v 
#               failure_regex: FAILED  
#         release_conf:                 # details how to build and release your repository
#             build_command: cd {repository_dir}; python setup.py sdist
#             upload_command: twine upload {repository_dir}/dist/* -u <username> -p <password
#             cleanup_command: rm -rf {repository_dir}/dist
```
#### API:
`curl -H "Content-Type: application/json" -X POST -d '<JSON_PAYLOAD>' http://<listen_address>:<port><subdomain>/`

The API supports the following POST requests:
- Trigger build and upload of the latest tag:
  - JSON payload `{"event":"new_tag","repository":"<repo_name>"}` 
- List repositories registered with the API:
  - JSON payload `{"event":"list_repositories"}`
- List all repository object attributes:
  - JSON payload `{"event":"list_repository","repository":"<repo_name>"}`
  
#### Notes
This program is written as a daemon process.
If you are going to be running it under systemd, create a unit that calls `py-build-server foreground`

