import yaml
import logging


class Config(object):
    def __init__(self):
        with open('/etc/py-build-server/config.yaml', 'r') as config_file:
            config = yaml.load(config_file)

        if isinstance(config, dict):
            self.logging = Logging(config.get('logging', {}))
            self.repos = {name: Repo(name, conf) for name, conf in
                          config.get('repositories', {}).items()}
            self.update_method = UpdateMethod(config.get('repository_update_method', 'polling'))
            self.api = Api(config.get('api', {}))

        self._sanity_check()
        logging.basicConfig(level=self.logging.level)

    def get(self, name):
        return self.repos.get(name)

    def _sanity_check(self):
        if len(self.repos) < 1:
            raise Exception(msg='no repos detected in yaml')
        for name, repo in self.repos.items():
            if repo.dir is None:
                raise Exception(msg='repo {} has no dir set'.format(name))


class UpdateMethod(object):
    class Method(object):
        def __init__(self, conf):
            self.subdomain = conf.get('subdomain')
            self.listen_address = conf.get('listen_address')
            self.port = conf.get('port')

    def __init__(self, conf):
        self.methods = {}
        for method in ('github_webhook', 'bitbucket_webhook'):
            if method in conf:
                c = conf.get(method)
                self.methods[method] = self.Method(c)
        if 'polling' in conf:
            self.methods['polling'] = 'polling'


class Logging(object):
    def __init__(self, conf):
        try:
            level_map = logging._nameToLevel
        except:
            level_map = logging._levelNames
        self.level = level_map.get(conf.get('level', 'info').upper())


class Repo(object):
    class Tests(object):
        def __init__(self, conf):
            self.command = conf.get('command')
            self.failure_regex = conf.get('failure_regex')
            self.success_regex = conf.get('success_regex')

    class ReleaseConf(object):
        def __init__(self, conf):
            self.build_command = conf.get('build_command')
            self.upload_command = conf.get('upload_command')
            self.cleanup_command = conf.get('cleanup_command')

    class RepositoryApi(object):
        def __init__(self, conf):
            self.type = conf.get('type')
            self.owner = conf.get('owner')
            self.username = conf.get('username')
            self.password = conf.get('password')
            self.target_url = conf.get('target_url')
            self.context = conf.get('context')
            self.name = conf.get('name')
            self.key = conf.get('key')

    def __init__(self, name, conf):
        self.name = name
        self.dir = conf.get('dir')
        self.fetch_frequency = conf.get('interval', 10)
        self.update_method = conf.get('update_method')
        self.remote = conf.get('remote', 'origin')
        self.release_conf = self.ReleaseConf(conf.get('release_conf'))
        self.tests = [self.Tests(t) for t in conf.get('tests', {})]
        if 'repository_api' in conf:
            self.repository_api = self.RepositoryApi(conf.get('repository_api'))


class Api(object):
    def __init__(self, conf):
        self.listen_address = conf.get('listen_address')
        self.subdomain = conf.get('subdomain')
        self.port = conf.get('port')
        self.strict_port_checking = conf.get('strict_port_checking', False)
