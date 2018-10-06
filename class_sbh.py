import xlrd
import scipy.constants as scc
import openpyxl
import numpy as np 
import os
import matplotlib.pyplot as plt

class Measurement:
    def __init__(self, filename):
        # string of excel file
        self.filename = filename 
        # workbook associated with filename
        self.workbook = xlrd.open_workbook(self.filename)
        # sheet associated with the measurement data
        self.data_sheet = self.workbook.sheet_by_index(0)
        # sheet associated with the measurement settings
        self.settings_sheet = self.workbook.sheet_by_index(2)
    
    def temperature(self, delim1="_", delim2="."):
        """ Called to get the temperature from a file name
        """
        # split the file string at each of "_" and make each split 
        # element part of a list
        temp = self.filename.split(delim1)
        # the last element of the split list will be for example, 220K.xls
        # split this element at the "." and save the 220K as the variable
        temp = temp[-1].split(delim2)[0]
        # return the temperature string with the "K" removed and convert
        # the remaining value to a float
        return float(temp[:-1])

    def test_name(self):
        """ Called to parse the settings sheet to the test name
        this is located in the first row and second column

        Ex: test name = vgs-id#1@1
        Strips everything but the vgs-id, or vds-id elements
        """
        return str(self.settings_sheet.cell_value(0,1)[:6])

    def executed(self):
        """ Called to get the time and date the measurement was 
        executed.
        """
        return str(self.settings_sheet.cell_value(6,1))

    def drain_voltage(self):
        """ Called to get the drain voltage for the measurement, this
        assumes that the value is constant throughout the measurement,
        if not, then there is another class-method to be used
        """
        if self.test_name() == "vgs-id":
            return float(self.settings_sheet.cell_value(14,2))
    
    def num_points(self):
        """ Called to get the number of points in a measurement
        """
        if self.test_name() == "vgs-id":
            return int(self.settings_sheet.cell_value(17,3))
        if self.test_name() == "vds-id":
            return int(self.settings_sheet.cell_value(17,2))
    
    def gate_step_size(self):
        """ Called to get the gate step size in the measurement
        """
        if self.test_name() == "vgs-id":
            return float(self.settings_sheet.cell_value(16,3))
        if self.test_name() == "vds-id":
            return int(self.settings_sheet.cell_value(16,3))
    
    def drain_step_size(self):
        """ Called to get the drain step size in the measurement
        """
        pass

    def rows(self):
        """ Called to get the number of rows of the excel file
        """
        return self.data_sheet.nrows

    def cols(self):
        """ Called to get the number columns of the excel file
        """
        return self.data_sheet.ncols

    def gate_voltage(self):
        """ Called to get the gate voltage for the measurement
        """
        voltages = []
        for col in range( self.cols() ):
            if self.data_sheet.cell_value( 0, col ) == "GateV":
                # start at 1 because row 0 is the doc headers
                for row in range( 1, self.rows() ):
                    voltages.append( self.data_sheet.cell_value( row, col ) )
        return voltages

    def max_gate_voltage(self):
        """ Called to get the max gate voltage for the measurement
        """
        return self.gate_voltage()[-1]

    def min_gate_voltage(self):
        """ Called to get the min gate voltage for the measurement
        """
        return self.gate_voltage()[0]

    def current(self):
        """ Called to get the current values for the measurement in Amps
        """
        current = []
        for col in range( self.cols() ):
            # start at 1 because row 0 is the doc headers
            if self.data_sheet.cell_value( 0, col ) == "DrainI":
                for row in range( 1, self.rows() ):
                    current.append( self.data_sheet.cell_value( row, col ) ) 
        return current

    def lnT_currnet(self, order=1.5):
        """ Called to get the current at each gate voltage value in the form 
        of Ln( I / T^(order) )

        Parameters
        ----------
        order : float
            order to which the temperature should be taken. default value 
            is 3/2. Other possible value is 2.0
        """
        return [ np.log( x / ( scc.k * self.temperature()**order ) )
                for x in self.current() ]

    def abs_current(self):
        """ Called to get the absolute value of the current values in Amps
        """
        return map(abs, self.current())

    def abs_normalized_current(self, width):
        """ Called to get the absolute value of the current divided by
        the width of the channel
        
        Parameters
        ----------
        width : float
            width of the device channel
        """
        return [ x / width for x in map(abs, self.current()) ]

    def normalize_current(self, width):
        """ Called to get the current divided by the width of the 
        channel

        Parameters
        ----------
        width : float
            width of the device channel
        """
        return [ x / width for x in self.current() ]

    def conductivity(self, length, width):
        """ Called to get the conductivity in uS, where
        S = I/Vds * L/W

        Parameters
        ----------
        length : float
            length of the device channel
        width : float
            width of the device channel
        """
        if self.test_name() == "vgs-id":
            return [ x * (1.0e6/self.drain_voltage()) * length/width
                    for x in self.current() ]
        else:
            return None
    
    def plot_transfer(self, save_name=""):
        pass
    
    def plot_conductivity(self, save_name=""):
        pass

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
    x = Measurement("vgs-id#9@_vds_100mV_vgs_-50_80V_T1S-nbwse2_L2D-mos2_vac04_280K.xls")
    x.plot_transfer()