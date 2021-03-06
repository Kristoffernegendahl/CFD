##1D linear convection
import matplotlib.pyplot as plt
import numpy
import time
import pickle
from numbapro import autojit, cuda, jit, float32



###1-D Nonlinear convection implemented using Numpy
def NonLinNumpy(u, un, nx, nt, dx, dt):

    ###Run through nt timesteps and plot/animate each step
    for n in range(nt): ##loop across number of time steps
        un[:] = u[:]
        u[1:] = -un[1:]*dt/dx*(un[1:]-un[:-1])+un[1:]
    
    return u

###1-D Nonlinear convection implemented using 'vanilla' Python
def NonLinVanilla(u, nx, nt, dx, dt):

    for n in range(nt):
        for i in range(1,nx-1):
            u[i+1] = -u[i]*dt/dx*(u[i]-u[i-1])+u[i]

    return u

###1-D Nonlinear convection implemented using Numba JIT compiler (similar to LLVM)
@autojit
def NonLinNumba(u,un, nx, nt, dx, dt):

    for n in range(nt):
        for i in range(1,nx):
            un[i] = -u[i]*dt/dx*(u[i]-u[i-1])+u[i]

    return un

###1-D Nonlinear convection implemented using NumbaPro CUDA-JIT
@jit(argtypes=[float32[:], float32, float32, float32[:]], target='gpu')
def NonLinCudaJit(u, dx, dt, un):
    tid = cuda.threadIdx.x
    blkid = cuda.blockIdx.x
    blkdim = cuda.blockDim.x
    i = tid + blkid * blkdim

    if i >= u.shape[0]:
        return

    un[i] = -u[i]*dt/dx*(u[i]-u[i-1])+u[i]


def main():
    ##System Conditions    
    nx = 8192
    nt = 300
    c = 1
    xmax = 15.0
    dx = xmax/(nx-1)
    sigma = 0.25
    dt = sigma*dx

    ##Initial Conditions for wave
    ui = numpy.ones(nx) ##create a 1xn vector of 1's
    ui[.5/dx:1/dx+1]=2 ##set hat function I.C. : .5<=x<=1 is 2
    un = numpy.ones(nx)    

    t1 = time.time()
    u = NonLinNumpy(ui, un, nx, nt, dx, dt)
    t2 = time.time()
    print "Numpy version took: %.6f seconds" % (t2-t1)
    numpytime = t2-t1
    #plt.plot(numpy.linspace(0,xmax,nx),u[:],marker='o',lw=2)
   
    t1 = time.time()
    u = NonLinNumba(ui, un, nx, nt, dx, dt)
    t2 = time.time()
    print "Numbapro Vectorize version took: %.6f seconds" % (t2-t1)
    vectime = t2-t1
    #plt.plot(numpy.linspace(0,xmax,nx),u[:],marker='o',lw=2)

    u = numpy.ones(nx)
    u[:] = ui[:]
    griddim = 320, 1
    blockdim = 768, 1, 1
    NonLinCudaJit_conf = NonLinCudaJit[griddim, blockdim]
    t1 = time.time()
    for t in range(nt):
        NonLinCudaJit(u, dx, dt, un)
    t2 = time.time()

    print "Numbapro Cuda version took: %.6f seconds" % (t2-t1)
    cudatime = t2-t1
    #plt.plot(numpy.linspace(0,xmax,nx),u[:],marker='o',lw=2)

    #f = open('times', 'a')
    #f.write(str(nx) + '\n')
    # f.write(str(numpytime) + '\n')
    # f.write(str(vectime) + '\n')
    #f.write(str(cudatime) + '\n')
    #f.close()

###Don't uncomment this unless nx < 500
#    t1 = time.time()
#    u = NonLinVanilla(ui, nx, nt, dx, dt)
#    t2 = time.time()
#    print "Vanilla version took: %.6f seconds" % (t2-t1)
#    
#    plt.plot(numpy.linspace(0,xmax,nx),u[:],marker='o',lw=2)
    #plt.show()


if __name__ == "__main__":
        main()
