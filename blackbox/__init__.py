'''
vocab:
experiment - 
run - 
state - 
record - 
context - 
overhead - 


HARD - 5. thread safety - lets think about what needs to be made thread safe 
- for now the best practice around this is a new run for process
- not sure how to get around that 


6. asynchronous writes through the serializer - kind of done - currently requires a forced 'backup' 
7. clearing and setting of overheads
DONE 8. set end_time in land

Scott's comments:
- Why did you have to make a new experiment?
'''

import sys, inspect, os, time, uuid, traceback
class Recorder():
    '''
    Blackbox Recorder.  

    Internal class for keeping state (i.e. current experiment and run)
    '''
    def __init__(self, serializer=None):
        '''
        Initialize an empty recorder.
        '''
        self.experiment = None
        self.run = None
        self.current_state = {}
        self.context = {}
        if serializer is None:
            self.serializer = ShelveSerializer()
        
        
    def set_experiment(self, name):
        '''
        Set the current experiment from the serializer
        '''
        if self.experiment:
            raise Exception('Experiment %s already initialized! Experiment %s not created!'%(self.experiment.name, name))   
        self.experiment = self.serializer.get_experiment(name, create_not_exists=True)

    def get_experiment(self, name):
        '''
        Get an experiment from the serializer.
        TODO - current behavior is to create the experiment if it doesn't exist. I don't think that's what we want
        '''
        return self.serializer.get_experiment(name, create_not_exists=False)
    
    def create_run(self, name=None, description=None, force=False):
        '''
        Create a new run.
        
        TODO: The way this is setup right now - you can overwrite a run potentially. Need to fix that.
        '''
        if self.run:
            raise Exception('Flight in progress! Please land first!')
        # TODO: Great example of how this is not thread safe! What happens if a thread creates this run in the meantime!
        # This run would overwrite it.   
        if name is None:
            name = uuid.uuid()
        elif not force and name in self.experiment.list_runs():
            raise Exception('Run %s already exists in this experiment'%(name))
        self.run = Run(name, description)
        
    def stop_run(self):
        '''
        Stop a run.
        '''
        
        if self.run is None:
            raise Exception('No flight to stop!')
        self.close()
        self.run.end_time = time.time()
        self.current_state = {}
        self.context = {}
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
        
    def save(self, level = 2, verbose = False):
        '''
        Save the current state. This by default adds the current line number, file and function name.
        Updates the experiment object as well with this run.
        TODO: make this update async - currently it is on the main calling thread
        TODO: add stack information
        '''
        #TODO: Get the current stack and pull necessary info from the calling functions
        # uncomment this to get stack frame info - it is extremely slow so it is toggled off
        # frame = inspect.stack()[level]
        # self.context.update({'module':frame[1],
        #                      'line':frame[2],
        #                      'function':frame[3]})
        self.current_state.update(self.context)
        self.run.add_state(self.current_state)
        if verbose:
            l = ["{}: {}".format(key,item) for key,item in self.current_state.iteritems()]
            l = "State Saved: {}".format(' '.join(l))
            print l
        # reset the current_state and the context
        self.context = {}
        self.current_state = {}
        self.serializer.save_run(self.experiment, self.run)

        
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
        self.runs = {}
        
    def get_run(self, name):
        '''
        Get a run.
        '''
        try:
            return self.runs[name]
        except:
            Exception('{} is not a run in this experiment!'.format(name))
        
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

    def dataframe(self):
        pass


class Serializer():
    '''
    Base class for a serializer. Serializer's are required to implement methods for getting experiments, getting runs, and updating experiments.
    
    TODO: Decide exactly what the interface on this should be. It's unclear at this point. For example, is list_runs too specific?
    '''
    def __init__(self):
        pass

    
    def open(self, experiment, description=None, create_not_exists=False):
        '''
        Open an experiment.

        If 'create_not_exists' is True and the experiment does not exist, it is created.
        '''
        raise NotImplementedError('get_experiment must be implemented '
                                  'by Serializer subclasses')

    def get_run(self, experiment, run):
        raise NotImplementedError('get_run must be implemented '
                                  'by Serializer subclasses')
    
    
    def save_run(self, experiment, run):
        '''
        Update the run in the specific experiment.
        '''
        raise NotImplementedError('update must be implemented '
                                  'by Serializer subclasses')

    def close_run(self, experiment, run):
        '''
        Close the run. Extremely important to do to guarantee that all run events are saved.
        '''
        raise NotImplementedError('close must be implemented '
                                  'by Serializer subclasses')
    
    def list_runs(self, experiment):
        '''
        List of runs for this experiment
        '''
        raise NotImplementedError('update must be implemented '
                                  'by Serializer subclasses')

    
    
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

def takeoff(name=None, description=None, force=False):
    '''
    Begin recording a run.
    '''
    return _recorder.create_run(name, description, force)

def land():
    '''
    Stop recording a run.
    '''
    _recorder.stop_run()

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

def save(verbose=False):
    '''
    Save the current state.
    '''
    #print "blackbox pid",os.getpid()
    _recorder.save(verbose=verbose)
        
def record(wrapped):
    '''
    Logging decorator. Appends a record of a function_call to the current run. 
    Note - this will get added to the run after the function is returned.
    '''
    def inner(*args, **kwargs):
        # This function call was made from one level up - so that's the level we save
        _recorder.save(level=2)
        t = time.time()
        result = wrapped(*args,**kwargs)
        #print 'in inner', wrapped.__name__
        _recorder.log('function_call',wrapped.__name__)
        _recorder.log('timestamp', time.time())
        _recorder.log('input', args)
        _recorder.log('duration', time.time()-t)
        _recorder.log('result', result)
        _recorder.save(level = 2)
        return result
    return inner




