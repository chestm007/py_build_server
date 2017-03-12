from multiprocessing import Process

import time

import cherrypy

from py_build_server.lib.logger import Logger


def get_updater(config):
    if 'polling' in config.update_method:
        return PollingUpdater()
    if 'webhook' in config.update_method:
        return GithubWebhookUpdater()


class Updater(object):
    def __init__(self):
        self.repositories = {}
        self.logger = Logger('polling-updater')

    def register_new_repo(self, repo):
        self.repositories[repo.name] = repo

    def start(self):
        raise NotImplementedError

    def check_repo(self, repo):
        raise NotImplementedError

    def load_config(self, config):
        pass


class GithubWebhookUpdater(Updater):
    class Root(object):
        @cherrypy.expose
        @cherrypy.tools.json_in()
        def index(self):
            request = cherrypy.request.json

    def __init__(self):
        super(GithubWebhookUpdater, self).__init__()
        self.subdomain = None

    def start(self):
        cherrypy.quickstart(self.Root(), self.subdomain)

    def load_config(self, config):
        cherrypy.server.socket_host = config.update_method.get('listen_address', '0.0.0.0')
        self.subdomain = config.update_method.get('subdomain', '/')

    def sanity_check(self):


class PollingUpdater(Updater):
    def __init__(self):
        super(PollingUpdater, self).__init__()
        self.processes = []


    def start(self):
        for repo in self.repositories.values():
            repo.logger.debug('creating PollingUpdater process for {}'.format(repo.name))
            p = Process(target=self.check_repo, args=(repo, ))
            p.start()
            self.processes.append(p)

        self.logger.debug('Finished creating processes for PollingUpdater')
        for p in self.processes:
            p.join()

    def check_repo(self, repo):
        while True:
            self.logger.info('Checking status of {}'.format(repo.name))
            if repo.config.branch is not None:
                if repo.config.branch != str(repo.active_branch):
                    raise Exception(msg='repository is not on the correct branch({} != {})'
                                    .format(repo.active_branch, repo.config.branch))

            status = repo.get_status()
            repo.latest_tag = [tag.name for tag in reversed(sorted(repo.tags)) if tag.name != 'origin'][0]
            if status.behind:
                repo.queue.put('new_tag')
            self.logger.debug('waiting {} minutes'.format(repo.config.fetch_frequency))
            try:
                time.sleep(repo.config.fetch_frequency * 60)
            except KeyboardInterrupt:
                self.logger.debug('exited while waiting to check repo again')
                return