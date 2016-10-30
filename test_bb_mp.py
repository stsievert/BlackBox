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
    for i in range(0,20):
        xi = .5*(xi+x/xi)
        blackbox.log('iter', i)
        blackbox.log('xi', xi)
        error(xi, true_root)
        blackbox.save(verbose=True)
    return xi

def error(x,y):
    '''
    compute the error
    '''
    err = abs(x-y)
    blackbox.log('error', err)
    return err

def test_par_runs(i):
    blackbox.takeoff(name='Newtons method worker:{}'.format(i), description='sample run', force=True)    
    r = newton(i)
    blackbox.land()
    return r

blackbox.set_experiment('SquareRootParallel')
pool = Pool(4)
result  = pool.map(test_par_runs, [2, 3, 4, 5])
pool.close()

exp = blackbox.get_experiment('SquareRootParallel')
print exp.list_runs()
run = exp.get_run('Newtons method worker:2')
print run.events


