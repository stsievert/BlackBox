import math
import blackbox
from multiprocessing import Pool

#@blackbox.record
def newton(x):
    '''
    Compute the square root of x.
    '''
    xi = 1
    true_root = math.sqrt(x)
    for i in range(0,500):
        xi = .5*(xi+x/xi)
        blackbox.log('iter', i)
        blackbox.log('xi', xi)
        error(xi, true_root)
        blackbox.save(verbose=False)
    return xi

def error(x,y):
    '''
    compute the error
    '''
    err = abs(x-y)
    blackbox.log('error', err)
    return err

def test_par_runs(i):
    blackbox.takeoff('worker:2', 'sample run', True)    
    r = newton(i)
    blackbox.land()
    return r

blackbox.set_experiment('SquareRootParallel')
#pool = Pool(4)
#result  = pool.map(test_par_runs, [2, 3, 4, 5])
#pool.close()
#pool.join()
test_par_runs(2)
#print result


exp = blackbox.get_experiment('SquareRootParallel')
runs = exp.list_runs()
for run in runs:
     run = exp.get_run(run)
     print len(run.events)


