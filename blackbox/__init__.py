'''
Main code file for blackbox.
'''
import sys, inspect, os, time, uuid, traceback
from MsgpackSerializer import MsgpackSerializer
from .types import Experiment, Run, Serializer


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
            self.serializer = MsgpackSerializer()
        else:
            self.serializer = serializer

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
        experiment = self.serializer.get_experiment(name, create_not_exists=False)
        return experiment
    
    def create_run(self, name, description=None, force=False):
        '''
        Create a new run.
        
        TODO: The way this is setup right now - you can overwrite a run potentially. Need to fix that.
        '''
        if self.run:
            raise Exception('Flight in progress! Please land first!')
        # TODO: Great example of how this is not thread safe! What happens if a thread creates this run in the meantime!
        # This run would overwrite it.   
        if not force and name in self.experiment.list_runs():
            raise Exception('Run %s already exists in this experiment'%(name))
        self.run = Run(name, description)
        
    def stop_run(self):
        '''
        Stop a run. Once a run is stopped, it can no longer be written to.
        '''
        if self.run is None:
            raise Exception('No flight to stop!')
        self.run.end_time = time.time()
        self.serializer.stop_run(self.experiment, self.run)
        self.current_state = {}
        self.context = {}
        self.flying = False
        self.run = None
  
    def log(self, key, item):
        '''
        Log a key to the current state.
        '''
        self.current_state[key] = item

    def update_context(key, name, remove=False, clear=False):
        '''
        Update a key in the context
        '''
        if remove:
            del context[key]
            return
        elif clear:
            context = {}
            return
        else:
            context[key] = name
        
    def save(self, level = 2, verbose = False):
        '''
        Save the current state. This by default adds the current line number, file and function name.
        Updates the experiment object as well with this run.

        TODO: add stack information, inspect is a very slow call! Alternatively, you can have the adding of this info be optional.
        '''
        #TODO: Get the current stack and pull necessary info from the calling functions
        #uncomment this to get stack frame info - it is extremely slow so it is toggled off
        # frame = inspect.stack()[level]
        # self.context.update({'module':frame[1],
        #                      'line':frame[2],
        #                      'function':frame[3]})
        self.current_state.update(self.context)
        self.run.add_state(self.current_state)
        if verbose:
            l = ["{}: {}".format(key,item) for key,item in self.current_state.iteritems()]
            l = "State Saved: {}".format(' '.join(l))
            print l, os.getpid()
        # reset the current_state. Note, the context SHOULD NOT be reset
        self.current_state = {}
        self.serializer.save_run(self.experiment, self.run)


    
_recorder = Recorder()
# Decorators

def set_experiment(name):
    '''
    Set the current experiment to record to. You can only set one experiment at a time.
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
    if not _recorder.experiment is None:
        _recorder.create_run(name, description, force)


def land():
    '''
    Stop recording a run.
    '''
    if not _recorder.experiment is None:
        _recorder.stop_run()

def log(key, value):
    '''
    Log a key value pair into the state.
    '''
    if not _recorder.experiment is None and not _recorder.run is None:
        _recorder.log(key,value)

def add_overhead(key, value):
    '''
    Add a key value pair to the context. The context will get added to each save until it is cleared.
    '''
    if not _recorder.experiment is None and not _recorder.run is None:
        _recorder.update_context(key, value)

def remove_overhead(key):
    '''
    Remove a key from the context.
    '''
    if not _recorder.experiment is None and not _recorder.run is None:
        _recorder.update_context(key, None, remove=True)

def empty_overhead():
    '''
    Clear the context that gets added on each save.
    '''
    if not _recorder.experiment is None and not _recorder.run is None:
        _recorder.update_context(key, None, clear=True)

def save(verbose=False):
    '''
    Save the current state. It will be handed over to the serializer to be logged.
    '''
    if not _recorder.experiment is None and not _recorder.run is None:
        _recorder.save(verbose=verbose)

def record(wrapped):
    '''
    Logging decorator. Appends a record of a function_call to the current run. 
    Note - this will get added to the run after the function is returned.
    '''
    def inner(*args, **kwargs):
        # This function call was made from one level up - so that's the level we save
        _recorder.save(level=2)
        ts = time.time()
        result = wrapped(*args,**kwargs)
        te = time.time()
        #print 'in inner', wrapped.__name__
        _recorder.log('function_call',wrapped.__name__)
        _recorder.log('time_called',ts)
        _recorder.log('time_ended', te)
        _recorder.log('input', args)
        _recorder.log('duration', te-ts)
        _recorder.log('result', result)
        _recorder.save(level = 2)
        return result
    return inner




