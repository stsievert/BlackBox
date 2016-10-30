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
    for i in range(0,1000):
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
    #blackbox.log('error', err)
    return err

def test_par_runs(i):
    r = newton(i)
    return r

blackbox.set_experiment('SquareRootPar3')
blackbox.takeoff(name='Newton method par %i'%(7), description='sample run', force=True)    
#pool = Pool(4)
#result  = pool.map(test_par_runs, [2, 3, 4, 5])
#pool.close()
print test_par_runs(8)
blackbox.land()


# exp = blackbox.get_experiment('SquareRootPar3')
# print exp.list_runs()
# run = exp.get_run('Newton method par 7')
# print run.events


