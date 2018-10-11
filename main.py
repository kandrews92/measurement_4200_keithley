from measurement import Measurement
from sbh import SBH
from qdafile import QDAfile
import matplotlib.pyplot as plt
import numpy as np
import os

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
    files = []; file_prefix = ['vgs-id', 'vds-id']
    # search other all files in current path
    for file in os.listdir( path ):
        if file.endswith( extension ) and "analyzed" not in file:
            # if it is a .xls file, then search the prefix list
            for prefix in file_prefix:
                if prefix in file:
                    files.append( file ) 
    return files

def main():
    # get the measurement files in the current path
    files = list_dir()
    # create a list of instances for each measurement file
    # each element is a different measurement
    measures = [ Measurement(file) for file in files ]
    x = Measurement(files[1], capacitance=1.262e-8, threshold_voltage=-1.0)
    #y = SBH(measurements)
    #y = SBH(measures)
    #y.write_analysis()
    print x.get_filename()
    qda = QDAfile()
    qda.data = np.asarray(x.current(0))
    qda.write(x.get_filename()+'.qda')
    

if __name__ == "__main__":
    main()


    