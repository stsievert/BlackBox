import math
import blackbox

blackbox.set_experiment('SquareRoot')
blackbox.takeoff(name='Newton method', description='sample run')
print "hello world"
blackbox.log('a', 1)
blackbox.bank()
#routine(3)

#blackbox.land()

# @record
# def newton(x):
#     '''
#     Compute the square root of x.
#     '''
#     xi = 1
#     true_root = math.sqrt(x)
#     for i in range(0,10):
#         xi = .5*(xi+x/xi)
#         host.log('iter', i)
#         host.log('xi', xi)
#         error(xi, true_root)
#         if i==1:
#             host.descend()
#             host.log('whats for lunch?','potatoes and toast')
#             dinner()
#             host.ascend()
#         if i==2:
#             dinner()
        

#         host.register()

# def error(x,y):
#     '''
#     compute the error
#     '''
#     err = math.abs(x-y)
#     log('error', err)
#     return err



# @record
# def dinner():
#     log('whats for dinner?', 'durians and mangoes')
    

# @record
# def dessert():
#     log('whats for dessert', 'turnips')


