import sys
import time

from multiprocessing import Process

from py_build_server.lib import ExtendedRepo
from py_build_server.config import Config
from py_build_server.lib.logger import Logger
from py_build_server.lib.twine_extentions import UploadCall, Twine
from py_build_server.lib.python_daemon import Daemon


class PyBuildServer(Daemon):
    def __init__(self, *args, **kwargs):
        super(PyBuildServer, self).__init__(*args, **kwargs)
        self.config = Config()
        self.logger = Logger('py-build-server')

    def run(self, *args, **kwargs):
        processes = []
        self.logger.info('Initializing processes...')
        for repo in ExtendedRepo.build_repos_from_config(self.config):
            self.logger.debug('creating process for {}...'.format(repo.name))
            p = Process(target=self.check_repo, args=(repo, ))
            self.logger.debug('starting process for {}...'.format(repo.name))
            p.start()
            processes.append(p)
            self.logger.debug('started process for {}'.format(repo.name))

        try:
            for p in processes:
                self.logger.debug('waiting for threads to return (shouldnt happen')
                p.join()
        except KeyboardInterrupt:
            self.logger.info('exiting')
            sys.exit(0)

    @staticmethod
    def check_repo(repo):
        while True:
            try:
                repo.logger.info('Checking status of {}'.format(repo.name))
                if repo.config.branch is not None:
                    if repo.config.branch != str(repo.active_branch):
                        raise Exception(msg='repository is not on the correct branch({} != {})'
                                            .format(repo.active_branch, repo.config.branch))

                status = repo.get_status()
                latest_tag = [tag.name for tag in reversed(sorted(repo.tags)) if tag.name != 'origin'][0]
                if status.behind:
                    repo.logger.info('pulling latest changes for {repo} from {remote}/{branch}'
                                     .format(repo=repo.name,
                                             remote=repo.get_remote().name,
                                             branch=repo.active_branch.name))

                    repo.get_remote().pull()
                Twine(repo).upload(UploadCall(repo.working_dir, repo.config.twine_conf), latest_tag)
                repo.logger.debug('waiting {} minutes before checking again'.format(repo.config.fetch_frequency))
                time.sleep(repo.config.fetch_frequency * 60)
            except KeyboardInterrupt:
                repo.logger.debug('exiting process for {}'.format(repo.name))
                break


def main(command):
    server = PyBuildServer('/etc/py-build-server/pid',
                           stdout='/var/log/py-build-server/stdout.log',
                           stderr='/var/log/py-build-server/stderr.log')
    if command == 'start':
        server.start()

    elif command == 'stop':
        server.stop()

    elif command == 'restart':
        server.restart()

    elif command == 'foreground':
        server.run()

if __name__ == '__main__':
    main(sys.argv[1])
