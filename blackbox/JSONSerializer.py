import sys, inspect, os, time,  traceback, random, string, shelve
import ujson as json
from .types import Experiment, Run, Serializer
        
class JSONSerializer():
    def __init__(self, directory='.experiments', backup=False):
        self.directory = os.path.abspath(directory)
        self.experiment = False
        self.fp = None
        self.event_buffer = []

    def get_experiment(self, name, description = None, create_not_exists=False):
        '''
        Shelve implementation of get_experiment. The experiment is stored in a shelve in the .experiments directory.
        '''
        # See this post: http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
        dir_path = os.path.join(self.directory, name)
        if not os.path.exists(os.path.join(dir_path, 'info.json')):
            print("doesnt exist")
            # If experiment directory does not exist
            if create_not_exists:
                if not os.path.isdir(dir_path):
                    try:
                        os.makedirs(dir_path)
                    except OSError:
                        # failed to makedir, let's check if it's a file
                        if not os.path.isdir(dir_path):
                            raise Exception('%s already exists as path. Please use a different directory name'%(dir_path))
                else:
                    print('dir path exists and is a dir')
                with open(os.path.join(dir_path,'info.json'), 'w') as fp:
                    start_time = time.time()
                    fp.write(json.dumps({'name':name, 'description':description, 'start_time':start_time}))
                    experiment = Experiment(name, description, start_time)
            else:
                raise Exception('Experiment %s does not exist'%(name))
        else:
            with open(os.path.join(dir_path,'info.json'),'r') as fp:
                info = json.load(fp)
                experiment = Experiment(info['name'], info['description'], info['start_time'])
        self.experiment = experiment
        return experiment

    def get_run(self, name):
        '''
        Get a run from a specific experiment.
        '''
        try:
            pass
        except:
            print(traceback.print_exc())
            exp.close()
            Exception('Run does not exist in this experiment')
        
    def save_run(self, run):
        '''
        Save a run from a specific experiment.
        '''
        if self.fp is None:
            self.fp = open(os.path.join(self.directory,'{}_{}'.format(self.experiment.name, run.name)),'wb', 4096)
        if len(self.event_buffer) < 1000:
            self.event_buffer.append(run.events[-1])
        else:
            self.fp.write(json.dumps(self.event_buffer))
            self.event_buffer = []

    def stop_run(self, run):
        self.fp.write(json.dumps(self.event_buffer))
        self.fp.close()
        
    def list_runs(self, experiment):
        '''
        Get a list of the runs belonging to this experiment
        '''
        try:
            exp = shelve.open(os.path.join(self.directory, experiment.name))
            run_names = list(exp.keys())
            exp.close()
        except Exception as e:
            print(traceback.print_exc())
            Exception('Error updating run!')
        run_names.remove('meta')
        return run_names

        

# So, look at the time we record the last piece of info. Any item in the queue whose time is before this time is invalidated!
# I think the async listener can't be a separate class. It needs info in the serializer!
# What happens if events gets added to while I am saving...
# So question - does every process spawn one of these threads? Or is there only one?
