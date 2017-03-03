from pepper import Pepper
from .settings import Settings

class SaltApi(object):
    def __init__(self):
        self.settings = Settings()
        self.api = Pepper(self.settings.get_variable('NUTS_SALT_REST_API_URL'))

    def connect(self):
        '''connects to the salt-api with the defined username and password.
        configuration can be done in config.yml in your cwd'''
        self.api.login(self.settings.get_variable('NUTS_SALT_REST_API_USERNAME'),
                       self.settings.get_variable('NUTS_SALT_REST_API_PASSWORD'), 'pam')
    def start_task(self, args):
        ''' starts a the function defined in args.function on targets (args.targets) with the parameters defined in args.arguments
        
            response format: {u'return': [{u'srv01':True,u'srv020:True}]}
        '''
        
        response = self.api.low([{'client': 'local', 'tgt': args['targets'], 'fun': args['function'],
                                  'arg': args['arguments']}])

        return response

    def start_task_async(self, args):
        ''' starts a the function defined in args.function on targets (args.targets) with the parameters defined in args.arguments
        this function is asnyc and you'll have to collect the results with get_task_result
        
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
    def get_task_result(self,taskresponse=None, taskid=None):
        '''returns the current result of the entered task.
        you can either insert the response you got when you started the task OR
        you can insert the taskid directly
        
        response format: {u'return': [{u'srv01':True,u'srv020:True}]}
        '''
        if taskid != None and taskresponse != None and  taskresponse['return'][0]['jid'] != taskid:
            #throw exception
            raise ValueError('You entered both taskresponse and taskid but they didn\'t match')
        if taskid == None:
            taskid = taskresponse['return'][0]['jid']
        return self.api.lookup_jid(taskid)