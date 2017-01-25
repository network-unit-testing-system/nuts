from pepper import Pepper
from .settings import Settings

class SaltApi(object):
    def __init__(self):
        self.settings = Settings()
        self.api = Pepper(self.settings.getVariable('NUTS_SALT_REST_API_URL'))

    def connect(self):
        '''connects to the salt-api with the defined username and password.
        configuration can be done in config.yml in your cwd'''
        self.api.login(self.settings.getVariable('NUTS_SALT_REST_API_USERNAME'),
                       self.settings.getVariable('NUTS_SALT_REST_API_PASSWORD'), 'pam')


    def start_task(self, args):
        ''' starts a the function defined in args.function on targets (args.targets) with the parameters defined in args.arguments
        
            response format: {u'return': [{u'jid': u'20160718141822884336', u'minions': [u'srv01']}]}
        '''
        
        response = self.api.low([{'client': 'local_async', 'tgt': args['targets'], 'fun': args['function'],
                                  'arg': args['arguments']}])

        return response
    
    def abort_task(self, args):
        '''aborts the task with the taskid defined in args.job_id'''
        response = self.api.low([{'client': 'local_async', 'tgt': '*', 'fun': 'saltutil.kill_job',
                                  'arg': [args.job_id]}])
        return response
    def get_job_result(self,jobresponse=null, jobid=null):
        '''returns the current result of the entered job.
        you can either insert the response you got when you started the task OR
        you can insert the jobid
        '''
        if jobid != null and jobresponse != null and  jobresponse['return'][0]['jid'] != jobid:
            #throw exception
            raise ValueError('You entered both jobresponse and jobid but they didn\'t match')
        if jobid == null:
            jobid = jobresponse['return'][0]['jid']
        return self.api.lookup_jid(jobid)