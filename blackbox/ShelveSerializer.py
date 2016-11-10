import sys, inspect, os, time, uuid, shelve, traceback, threading
from multiprocessing import Manager, Queue, RLock

_queue = Queue()


class AsyncListener():
    '''
    Fairly general purpose asynchronous daemon.
    See: http://stackoverflow.com/questions/641420/how-should-i-log-while-using-multiprocessing-in-python/894284#894284

    for a similar implemenation in logging.
    '''
    def __init__(self, serializer):
        self.serializer = serializer
        print "serializer in AsyncListener", self.serializer
        self.t = threading.Thread(target=self.process)
        self.t.daemon = True
        self.a = {}
        
    def start(self):
        self.t.start()
        
    def process(self):
        while True:
            try:
                s = _queue.get()
                experiment, run = s#self.queue.get()
                self.serializer._save(experiment, run)
                if not run.name in self.a.keys():
                    self.a[run.name] = 0
                self.a[run.name] +=1
                print "listener pid",os.getpid(), self.a[run.name]
            except EOFError:
                break
            except:
                raise
            
    def put(self, experiment, run):
        _queue.put((experiment, run))
        


class ShelveSerializer(Serializer):
    def __init__(self, directory='.experiments'):
        self.directory = os.path.abspath(directory)
        self.parallel_write = True

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
        return experiment

    def get_run(self, experiment, name):
        '''
        Get a run from a specific experiment.
        '''
        try:
            exp = shelve.open(os.path.join(self.directory, experiment.name))
            run = exp[name]
            exp.close()
            return run
        except:
            print traceback.print_exc()
            exp.close()
            Exception('Run does not exist in this experiment')
        
    def save_run(self, experiment, run):
        '''
        Save a run from a specific experiment.
        '''
        if self.parallel_write:
            _listener.put(experiment, run)
        else:
            self._save(experiment, run)
        # So, look at the time we record the last piece of info. Any item in the queue whose time is before this time is invalidated!
        # I think the async listener can't be a separate class. It needs info in the serializer!
        # What happens if events gets added to while I am saving...
        # So question - does every process spawn one of these threads? Or is there only one?

        
    def _save(self, experiment, run):
        try:
            exp = shelve.open(os.path.join(self.directory, experiment.name))
            #print 'save_run', run.name, type(run.name), exp.keys(), experiment.name
            exp[run.name] = run
            exp.close()
        except Exception,e:
            print e
            print traceback.print_exc()
            Exception('Error updating run!')

            
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


_listener = AsyncListener(_recorder.serializer)
_listener.start()
