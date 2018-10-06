from measurement import Measurement
from measurement import SBH
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
        if file.endswith( extension ):
            # if it is a .xls file, then search the prefix list
            for prefix in file_prefix:
                if prefix in file:
                    files.append( file ) 
    return files

if __name__ == "__main__":
    # get the measurement files in the current path
    files = list_dir()
    # create a list of instances for each measurement file
    # each element is a different measurement
    measurements = [ Measurement(file) for file in files ]
    x = Measurement(files[1])
    x.plot_conductivity()
    #sbh = SBH(measurements)

    