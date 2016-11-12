import math
import blackbox


@blackbox.record
def func():
    blackbox.log('var_in_func', 3)
    return 3

blackbox.set_experiment('ExampleExperiment')

blackbox.takeoff('Run 1', force=True)
blackbox.log('run_1_var', 1)
blackbox.save()
blackbox.land()

blackbox.takeoff('Run 2', force=True)
blackbox.log('run_2_var', 2)
func()
blackbox.save()
blackbox.land()

exp = blackbox.get_experiment('ExampleExperiment')
for run in exp.list_runs():
    run = exp.get_run(run)
    print '{} events'.format(run.name)
    for e in run.events:
        print e
