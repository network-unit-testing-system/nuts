from pepper import Pepper
from .settings import Settings

class SaltApi(object):
    def __init__(self):
        self.settings = Settings()
        self.api = Pepper(self.settings.getVariable('NUTS_SALT_REST_API_URL'))

    def connect(self):
        self.api.login(self.settings.getVariable('NUTS_SALT_REST_API_USERNAME'),
                       self.settings.getVariable('NUTS_SALT_REST_API_PASSWORD'), 'pam')

    def discovery(self, args):
        response = self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'state.sls',
                                  'arg': ['staging.discovery', 'concurrent=True',
                                          'pillar={"IP_Address":"%s"}' % args.ip]}])
        return response

    def start_task(self, args):
        response = self.api.low([{'client': 'local_async', 'tgt': '*', 'fun': 'state.sls',
                                  'arg': ['staging', 'concurrent=True', 'pillar={"SN":"%s"}' % args.sn]}])

        # response format: {u'return': [{u'jid': u'20160718141822884336', u'minions': [u'srv01']}]}
        return response

    def event(self, args):
        # creates event: salt/netapi/hook/osr/stagingtask/FCZ0000012Z9/rebooted
        response = self.api.low({'sn': args.sn, 'name': args.name},
                                path='/hook/osr/stagingtask/%s/%s' % (args.sn, args.name))
        return response

    def show_low_sls(self):
        response = self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'state.show_low_sls',
                                  'arg': [settings.OSR_SALT_STAGINGTASK_STATENAME, 'concurrent=True']}])
        return response

    def abort_task(self, args):
        response = self.api.low([{'client': 'local_async', 'tgt': '*', 'fun': 'saltutil.kill_job',
                                  'arg': [args.job_id]}])
        return response