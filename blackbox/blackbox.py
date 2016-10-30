'''
vocab:
experiment - 
run - 
state - 
record - 
context - 
overhead - 

'''

import sys, inspect, os, time, uuid, shelve, traceback

class Recorder():
    '''
    Blackbox Recorder.  

    HMM - this is highly stateful - might make more sense to have multiple recorders?
    '''
    def __init__(self):
        '''
        Initialize an empty recorder.
        '''
        self.experiment = None
        self.run = None
        self.current_state = {}
        self.context = {}
        self.serializer = ShelfSerializer()
        self.flying = False

    def set_experiment(self, name):
        '''
        Set the current experiment from the serializer
        '''

        if self.experiment:
            raise Exception('Experiment %s already initialized!'%(self.experiment.name))   
        self.experiment = self.serializer.get_experiment(name)

    def get_experiment(self, name):
        '''
        Get an experiment from the serializer.
        TODO - current behavior is to create the experiment if it doesn't exist. I don't think that's what we want

        '''
        return self.serializer.get_experiment(name)
    
    def create_run(self, name=None, description=None):
        '''
        Create a new run.
        
        TODO: The way this is setup right now - you can overwrite a run potentially. Need to fix that.
        '''
        if self.run:
            raise Exception('Flight in progress! Please land first!')

        if name is None:
            name = uuid.uuid()
        self.run = Run(name, description)
        self.flying = True
        
        
    def stop_run(self):
        '''
        Stop a run.
        '''
        
        if self.run is None:
            raise Exception('No flight to stop!')
        self.run.end_time = time.time()
        self.flying = False
        self.run = None
        
    def log(self, key, item):
        '''
        Log a key to the current state.
        '''
        self.current_state[key] = item

    def update_context(key, name):
        '''
        Update a key in the context
        '''
        context[key] = name
        
    def bank(self, level = 1):
        '''
        Bank the current state. This by default adds the current line number, file and function name.
        Updates the experiment object as well with this run.
        TODO: make this update async - currently it is on the main calling thread
        '''
        # Get the current stack and pull necessary info from the calling functions
        frame = inspect.stack()[level]
        self.context.update({'module':frame[1],
                        'line':frame[2],
                        'function':frame[3]})
        self.current_state.update(self.context)
        
        self.run.add_state(self.current_state)
        # reset the current_state and the context
        
        self.context = {}
        self.current_state = {}
        # Is this the right way to do this?
        # Do I even need an experiment object floating around?
        self.serializer.update_run(self.experiment, self.run)
        
class Serializer():
    '''
    Base class for a serializer. Serializer's are required to implement methods for getting experiments, getting runs, and updating experiments.
    '''
    def __init__(self):
        pass
    
    def get_experiment(self, name):
        raise NotImplementedError('get_experiment must be implemented '
                                  'by Serializer subclasses')

    def get_run(self, experiment, name):
        raise NotImplementedError('get_run must be implemented '
                                  'by Serializer subclasses')
    
    def update_run(self, experiment, run):
        '''
        Update the run in the specific experiment.
        '''
        raise NotImplementedError('update must be implemented '
                                  'by Serializer subclasses')

    
class ShelfSerializer(Serializer):
    def __init__(self, directory='.experiments'):
        self.directory = os.path.abspath(directory)
            
    def get_experiment(self, name, description = None):
        # See this post: http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
        # check for experiment in directory
        if os.path.exists(os.path.join(self.directory, name)) :
            exp_shelf = shelve.open(experiment)
            meta = exp_shelf['meta']
            experiment = Experiment(name, meta['description'],meta['start_time'])
            exp_shelf.close()
        else:
            # if it doesn't exist create this object, shelve it, and return
            if not os.path.isdir(self.directory):
                try:
                    os.makedirs(self.directory)
                except OSError:
                    if not os.path.isdir(path):
                        raise Exception('%s already exists as path. Please use a different directory name'%(self.directory))
            exp_shelf = shelve.open(os.path.join(self.directory,name))
            start_time = time.time()
            exp_shelf['meta'] = {'name':name, 'description': description, 'start_time':start_time}
            exp_shelf.close()
            experiment = Experiment(name, description, start_time)
        return experiment

    def get_run(self, experiment, name):
        try:
            exp = shelve.open(os.path.join(self.directory, experiment.name))
            run = exp[name]
            exp.close()
        except:
            exp.close()
            Exception('Run does not exist in this experiment')
        exp.close()
        
    def update_run(self, experiment, run):
        print "updating run"
        try:
            exp = shelve.open(os.path.join(self.directory, experiment.name))
            exp[run.name] = run
            exp.close()
        except Exception,e:
            print traceback.print_exc()
            Exception('Error updating run!')

            
class Experiment():
    '''
    Main experiment class.
    
    Used for accessing information about an experiment.
    '''
    def __init__(self, name, description, start_time):
        '''
        Initialize a new experiment object. 
        '''
        self.name = name
        self.description = description
        self.start_time = time.time()
        self.serializer = ShelfSerializer()
        self.runs = {}
        
    def get_run(self, name):
        '''
        Get a run.
        '''
        if name in runs.keys():
            return runs[name]
        else:
            run = serializer.get_run(self, name)
            self.runs[name] = run            
        return run 

class Run():
    '''
    Main run class.
    '''
    def __init__(self, name, description):
        '''
        Initialize a new Run object. 
        '''
        self.name = name
        self.description = description
        self.start_time = time.time()
        self.end_time = None
        self.events = []

    def add_state(self, state):
        '''
        Add a state to the current set of states. 
        '''
        state.update({'timestamp': time.time()})
        self.events.append(state)

_recorder = Recorder()

def set_experiment(name):
    '''
    Set the current experiment to record to.
    '''
    _recorder.set_experiment(name)

def get_experiment(name):
    '''
    Get an experiment.
    '''
    return _recorder.get_experiment(name)

def takeoff(name=None, description=None):
    '''
    Begin recording a run.
    '''
    # TODO: what happens is there is a run currently?
    return _recorder.create_run(name, description)

def land():
    '''
    Stop recording a run.
    '''
    _recorder.stop_run()

#TODO: it is not clear why status is being exposed, or why it even exists.
def log(key, value):
    '''
    Log a key value pair into the state.
    '''
    _recorder.log(key,value)

def overhead(key, value):
    '''
    Add a key value pair to the context.
    '''
    _recorder.update_context(key, value)

def bank():
    '''
    Bank the current state.
    '''
    _recorder.bank()
        
def record(wrapped):
    '''
    Logging decorator. Appends a record of a function_call to the current run. 
    Note - this will get added to the run after the function is returned.
    '''
    def inner(*args, **kwargs):
        # This function call was made from one level up - so that's the level we bank
        _recorder.bank(level=2) 
        _recorder.log('function_call',wrapped.__name__)
        _recorder.log('timestamp', time.time())
        _recorder.log('input', args)
        t = time.time()
        result = wrapped(*args,**kwargs)
        _recorder.log('result', result)
        _recorder.log('duration', time.time())
        _recorder.bank(level = 2)
        return result
    return inner

