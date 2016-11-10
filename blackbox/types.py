import time

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

    def get_run(self, run):
        raise NotImplementedError('get_run must be implemented '
                                  'by Serializer subclasses')
    
    
    def save_run(self, run):
        '''
        Update the run in the specific experiment.
        '''
        raise NotImplementedError('update must be implemented '
                                  'by Serializer subclasses')

    def stop_run(self, run):
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
