import math
import blackbox

blackbox.experiment('SquareRoot')
flight = blackbox.flight(name='Newton method',description='sample run')

flight.takeoff()
newton(2)
flight.cruise()
# since we are cruising, nothing wil get logged.
routine(3)

flight.stop()

@record
def newton(x):
    '''
    Compute the square root of x.
    '''
    xi = 1
    true_root = math.sqrt(x)
    for i in range(0,10):
        xi = .5*(xi+x/xi)
        host.log('iter', i)
        host.log('xi', xi)
        error(xi, true_root)
        if i==1:
            host.descend()
            host.log('whats for lunch?','potatoes and toast')
            dinner()
            host.ascend()
        if i==2:
            dinner()
        

        host.register()

def error(x,y):
    '''
    compute the error
    '''
    err = math.abs(x-y)
    log('error', err)
    return err



@record
def dinner():
    log('whats for dinner?', 'durians and mangoes')
    

@record
def dessert():
    log('whats for dessert', 'turnips')


'''
RECORD: So here is what is recorded 
'''

record = {'experiment_name': 'SquareRoot'
          {'flight_name':'Newton method',
           'description':'sample run',
           'events':[{'function_call':'newton',
                      'events':[{'iter':0, 'xi':1.5, 'err':.085786},
                                {'iter':1, 'xi':1.416, 'err':.00245, 'events':[{'whats for lunch':'potatoes and toast',
                                                                                'events':[{'function_call':'dinner',
                                                                                           'events':[{ 'whats for dinner?':'durians and mangoes'}]
                                                                                }]}]},
                                {'iter':2, 'xi':, 'err':1.4142, 'err':.000011, 'events':[{'function_call':'dinner',
                                                                                          'events':[{ 'whats for dessert?':'turnips'}]}]}
                                ]
                      }]
          }
}
