import sys, inspect, os, time, uuid, shelve, traceback, threading
from multiprocessing import Manager, Queue, RLock
from .types import Experiment, Run, Serializer
_queue = Queue()


class AsyncListener():
    '''
    Fairly general purpose asynchronous daemon.
    See: http://stackoverflow.com/questions/641420/how-should-i-log-while-using-multiprocessing-in-python/894284#894284

    for a similar implemenation in logging.
    '''
    def __init__(self):
        self.t = threading.Thread(target=self.process)
        self.t.daemon = True
        
    def start(self):
        self.t.start()
        
    def process(self):
        timestamps = {}
        while True:
            try:
                s = _queue.get()
                directory, experiment, run, timestamp = s
                # Only save the run if the timestamp on it is greater than the last time we saved
                if not run.name in timestamps.keys() or timestamp > timestamps[run.name]:
                    ShelveSerializer._save(directory, experiment, run)
                    timestamps[run.name] = time.time()                   
            except EOFError:
                break
            except:
                raise
            
    def put(self, directory, experiment, run, timestamp):
        _queue.put((directory, experiment, run, timestamp))

_listener = AsyncListener()
_listener.start()
        
class ShelveSerializer():
    def __init__(self, directory='.experiments', backup=False):
        self.directory = os.path.abspath(directory)
        self.experiment = False
        self.backup=False
        
    def get_experiment(self, name, description = None, create_not_exists=False):
        '''
        Shelve implementation of get_experiment. The experiment is stored in a shelve in the .experiments directory.
        '''
        # See this post: http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
        # check for experiment in directory
        if os.path.exists(os.path.join(self.directory, name+'.db')) :
            exp_shelf = shelve.open(os.path.join(self.directory, name))
            meta = exp_shelf['meta']
            experiment = Experiment(name, meta['description'],meta['start_time'])
            exp_shelf.close()
        elif create_not_exists:
            # if it doesn't exist create this object, shelve it, and return
            if not os.path.isdir(self.directory):
                try:
                    os.makedirs(self.directory)
                except OSError:
                    # failed to makedir, let's check if it's a file
                    if not os.path.isdir(path):
                        raise Exception('%s already exists as path. Please use a different directory name'%(self.directory))
            exp_shelf = shelve.open(os.path.join(self.directory,name))
            start_time = time.time()
            exp_shelf['meta'] = {'name':name, 'description': description, 'start_time':start_time}
            exp_shelf.close()
            experiment = Experiment(name, description, start_time)
        else:
            raise Exception('Experiment %s does not exist'%(name))
        self.experiment = experiment
        return experiment

    def get_run(self, name):
        '''
        Get a run from a specific experiment.
        '''
        try:
            exp = shelve.open(os.path.join(self.directory, self.experiment.name))
            run = exp[name]
            exp.close()
            return run
        except:
            print traceback.print_exc()
            exp.close()
            Exception('Run does not exist in this experiment')
        
    def save_run(self, run):
        '''
        Save a run from a specific experiment.
        '''
        if self.backup:
            _listener.put(self.directory, self.experiment, run, time.time())

    def stop_run(self, run):
        _listener.put(self.directory, self.experiment, run, time.time())


    def list_runs(self, experiment):
        '''
        Get a list of the runs belonging to this experiment
        '''
        try:
            exp = shelve.open(os.path.join(self.directory, experiment.name))
            run_names = exp.keys()
            exp.close()
        except Exception,e:
            print traceback.print_exc()
            Exception('Error updating run!')
        run_names.remove('meta')
        return run_names

        
    @staticmethod
    def _save(directory, experiment, run):
        try:
            exp = shelve.open(os.path.join(directory, experiment.name))
            exp[run.name] = run
            exp.close()
        except Exception,e:
            print e
            print traceback.print_exc()
            Exception('Error updating run!')
    


# So, look at the time we record the last piece of info. Any item in the queue whose time is before this time is invalidated!
# I think the async listener can't be a separate class. It needs info in the serializer!
# What happens if events gets added to while I am saving...
# So question - does every process spawn one of these threads? Or is there only one?
