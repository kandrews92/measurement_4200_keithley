from measurement_4200_keithley.measurement import Measurement
from measurement_4200_keithley.sbh import SBH
from measurement_4200_keithley.plotmeasurement import PlotMeasurements
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os, os.path

def list_dir( extension=".xls", path="."):
    """ Called to list the excel files in the current path. Ignores all files
    that may be excel files but are not measurement files

    Parameters
    ----------
    extension : string
        file extension, typically .xls or .xlsx
    path : string
        file path to search 
    """
    # measurement prefixes to search for
    files = []; file_prefix = ['vgs-id', 'vds-id', 'res2t']
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in [f for f in filenames if f.endswith(extension) ]:
            # skip any analyzed files
            if "analyzed" not in filename:
                # skip any excel files that are not data measurements
                for prefix in file_prefix:
                    if prefix in filename:
                        files.append(os.path.join(dirpath, filename) )
    return files

def plot_conductivity_temperature(measurements):
    """ Plot several temperatures at one """
    for i in range( len(measurements) ):
        plt.plot( measurements[i].gate_voltage(), measurements[i].conductivity(), label='T = '+str(measurements[i].temperature())+' K' )
    plt.ylabel(r'$\sigma_{2\mathrm{D}}\,(\mu\mathrm{S})$', fontsize=16)
    plt.xlabel(r'$V_\mathrm{gs}\,(\mathrm{V})$', fontsize=16)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()

def plot_transfer_temperature(measurements, log=False):
    """ Plot several temperatures at once """
    import matplotlib.pyplot as plt 
    import matplotlib as mpl
    for i in range( len(measurements) ):
        if log == True:
            plt.semilogy( measurements[i].gate_voltage(), measurements[i].current(), label='T = '+str(measurements[i].temperature())+' K' )
        else:
            plt.plot( measurements[i].gate_voltage(), measurements[i].current(units='uA'), label='T = '+str(measurements[i].temperature())+' K' )
    if log == True:
        plt.ylabel(r'$I_\mathrm{ds}\,(\mathrm{A})$', fontsize=16)
    else:
        plt.ylabel(r'$I_\mathrm{ds}\,(\mu\mathrm{A})$', fontsize=16)
    plt.xlabel(r'$V_\mathrm{gs}\,(\mathrm{V})$', fontsize=16)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.show()

def plot_conductivity_transfer(measurements):
    """ Plot several temperatures at once """
    import matplotlib.pyplot as plt 
    import matplotlib as mpl 
    for i in range( len(measurements) ):
        if measurements[i].temperature > 280.0:
            idx = i
    fig, ax1 = plt.subplots()
    ax1.semilogy(measurements[idx].gate_voltage(), measurements[idx].current(), 'r')
    ax1.set_ylabel(r'$I_\mathrm{ds}\,(\mathrm{A})$', fontsize=16, color='r')
    ax1.tick_params('y', colors='r')
    ax1.set_xlabel(r'$V_\mathrm{gs}\,(\mathrm{V})$', fontsize=16)
    ax2 = ax1.twinx()
    ax2.plot(measurements[idx].gate_voltage(), measurements[idx].conductivity(), 'b')
    ax2.set_ylabel(r'$\sigma_{2\mathrm{D}}\,(\mu\mathrm{S})$', color='b', fontsize=16)
    ax2.tick_params('y', colors='b')
    fig.tight_layout()
    plt.show()

def main():
    """ main loop: contains some example calls and manipulations """
    # get the measurement files in the current path and subpaths
    files = list_dir()
    # output the files list
    for f in files: print "file: %s\n" %(f) 

    # create a list of instances for each measurement found
    # access each measurement through m[0], m[1],..., m[len(file)-1]
    # this is initialized with default values, such as length, width,
    # capacitance, and threshold voltage. 
    m = [ Measurement(file) for file in files ]

    # set device parameters
    L = 5.2        # [micrometers]
    W = 4.3         # [micrometers]
    C = 1.262e-8        # [F/cm^2] (capacitance/area)
    Vth = -2.5          # [Volts]
    # create list of instances with non-default values in the 
    # constructor
    n = [ Measurement(file, length=L, width=W, capacitance=C, \
           threshold_voltage=Vth) for file in files ]
    
    # use of __str__ or __repr__ overloading
    for item in n: print item
    
    # use of measurement type method
    print "\nn[0] test_name: %s\n" %(n[0].test_name())

    # use of temperature method
    # use of current method and indexing
    # use of gate voltage method
    # get it in microAmps and get the last value
    for item in n: 
        print "T = %f K; I_ds = %f uA @ V_gs = %f V & V_ds = %f; " \
        %(item.temperature(), item.current(-1, units='uA'), \
        item.gate_voltage(-1), item.drain_voltage())
    
    # show some plotting tests
    plot_conductivity_temperature(n)
    plot_transfer_temperature(n)
    plot_conductivity_transfer(n)



    # TODO: 
    # add examples using SBH class

if __name__ == "__main__":
    main()


    
