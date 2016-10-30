import math
import blackbox

@blackbox.record
def newton(x):
    '''
    Compute the square root of x.
    '''
    xi = 1
    true_root = math.sqrt(x)
    for i in range(0,10):
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

blackbox.set_experiment('SquareRoot')

for i in range(10):
    blackbox.takeoff(name='Newton method %i'%(i), description='sample run for %i'%(i), force=True)
    newton(i)
    blackbox.land()


#exp = blackbox.get_experiment('SquareRoot')
#print exp.list_runs()
#run = exp.get_run('Newton method 1')
#print run.events
'''
As of right now, its not clear how this would handle multiple threads. It's also not clear what should be locked to handle multithreading effectively.


'''
