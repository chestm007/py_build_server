An automated build server written for Python2.7 (python3 support coming soon)

####About
monitors git repository either by polling or listening for webhook messages, and when new tagged versions are released, builds and uploads to your chosen repository via twine

####Installation
`sudo pip2 install py-build-server`

you will need to modify `config.yaml` file in `/etc/py-build-server/` to match your deployment:

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
#     listen_address: 127.0.0.1      # listen on this address
#     strict_port_checking: true     # (O) setting to false may let the api accept requests intended
#                                    #     for another module
#     port: 9832                     # port to listen on
#     subdomain: /api                # subdomain to bind to
#
### this section defines how to check for changes
#
# repository_update_method: polling  # (O) poll git repo
# repository_update_method:          # (O) --alternatively--
#     github_webhook:                # (O) specify webhook to recieve notifications from github
#         subdomain: /github         # listen to this subdomain (http://<your_url/)
#         listen_address: 192.168.1.2# listen on this address
#
### this section set logging options
#
# logging:                           # (O)
#     level: debug                   # (O) DEBUG|WARN|INFO|ERROR|OFF (case doesnt matter)
#     implement_journald: false      # (O) send logs to journald instead
#
### this section sets repository specific settings
# repositories:
#     repo_one:  # needs to match github if using webhooks
#         dir: /path/to/repository/root
#         interval: 10               # (O) minutes between repo checks (only needed if polling)
#         remote: origin             # (O) remote name to fetch (default: origin)
#         branch: branch_to_release  # (O) if set, dont upload unless on this branch
#         twine_conf:                # this whole section of options are optional, but you will need
#                                    # to supply user/pass or pypirc file
#             username: user         # (O) username to authenticate to repository as
#             password: pass         # (O) password to authenticate to repository with
#             repository:            # (O) repo to upload to (default: pypi)
#             gpg_sign: true|false   # (O) sign files to upload using gpg
#             gpg_program:           # (O) program used to sign uploads(default: gpg)
#             gpg_identity:          # (O) gpg identity used to sign files
#             comment:               # (O) comment to include with distribution file
#             pypirc_file:           # (O) the .pypirc file to use
#             skip_existing: false   # (O) continue uploading if one already exists
```
#### API:
The API supports the following POST requests:
- Trigger build and upload of the latest tag:
  - The JSON payload should look like `{"event":"new_tag","repository":"<repo_name>"}` 
  - eg: `curl -H "Content-Type: application/json" -X POST -d '{"event":"new_tag","repository":"py_build_server"}' http://localhost:9832/api/`
  
####Notes
This program is written as a daemon process.
If you are going to be running it under systemd, create a unit that calls `py-build-server foreground`

