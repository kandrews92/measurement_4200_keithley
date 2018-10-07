import xlrd
import xlwt
import scipy.constants as scc
import openpyxl
from xlutils.copy import copy as xl_copy
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import OrderedDict

class Measurement:
    """ Class that manipulates excel files produced from measurements
    on a Keithley 4200 semiconductor analyzer. 

    The excel files that this class should be used with have a specific
    file name format that should be used. If not used, then this class
    will not work as intented. 

    The file format is: 
        "[test name]_[measurement_number]_[voltage_range]_[temperature].xls"
        e.g. 'vgs-id#9@_vds_1V_vgs_-50_80V_T1S_L2D_vac04_280K.xls'
    
    The excel file then has three sheets:
        1) "Data"
            -Contains the actual measurement data with row 0 
            being the column headers
        2) "Calc"
            -Initially this is blank
        3) "Settings"
            -Contains the settings used for the particular measurement
    
    For a brief description of each class method see each method's
    docstring. 
    """
    def __init__(self, filename, width=1.0, length=1.0):
        # string of excel file
        self.filename = filename 
        # workbook associated with filename
        try:
            self.workbook = xlrd.open_workbook(self.filename)
        except IOError:
            self.workbook = None
            print "No filename: %s found" %( self.filename )
        except NameError:
            self.workbook = None
            print "Package: xlrd not imported"
        # sheet associated with the measurement data
        try:
            self.data_sheet = self.workbook.sheet_by_index(0)
        except AttributeError:
            self.data_sheet = None
        # sheet associated with calculations
        try:
            self.calc_sheet = self.workbook.sheet_by_index(1)
        except AttributeError:
            self.calc_sheet = None
        # sheet associated with the measurement settings
        try:
            self.settings_sheet = self.workbook.sheet_by_index(2)
        except AttributeError:
            self.settings_sheet  = None
        self.width = width 
        self.length = length
    
    def width(self):
        """ Called to get the width of the device 
        """
        return self.width

    def length(self):
        """ Called to get the length of the device
        """
        return self.length

    def write_analysis(self):
        # TODO
        pass
    
    def __repr__(self):
        """ Called when user prints instance of class, mainly in 
        interactive environment, e.g. 
        >>> x = Measurement(file) 
        >>> x # __repr__ would be called here
        """
        return "<Measurement \n\tfilename:%s\n\tworkbook:%s\n\tdata sheet:%s\
            \n\tcalc sheet:%s\n\tsettings sheet:%s >" \
             %(self.filename, self.workbook, self.data_sheet, \
             self.calc_sheet, self.settings_sheet)

    def __str__(self):
        """ Called when user print instance of class
        e.g.
        >>> x = Measurement(file)
        >>> print x # __str__ would be called here
        """
        return self.__repr__()

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
        try:
            return float(temp[:-1])
        except ValueError:
            return None

    def test_name(self):
        """ Called to parse the settings sheet to the test name
        this is located in the first row and second column

        Ex: test name = vgs-id#1@1
        Strips everything but the vgs-id, or vds-id, or res2t elements
        """
        try:
            return str(self.settings_sheet.cell_value(0,1)[:6])
        except AttributeError:
            return None

    def executed(self):
        """ Called to get the time and date the measurement was 
        executed.
        """
        try:
            return str(self.settings_sheet.cell_value(6,1))
        except AttributeError:
            return None

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
        if self.test_name() == 'res2t':
            pass
    
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
        # drain step size for 'vgs-id' = drain_voltage()
        # drain voltage is held constant in this measurement
        if self.test_name() == "vgs-id":
            return self.drain_voltage()

    def __rows(self):
        """ Called to get the number of rows of the excel file
        """
        try:
            return self.data_sheet.nrows
        except AttributeError:
            return None 

    def __cols(self):
        """ Called to get the number columns of the excel file
        """
        try: 
            return self.data_sheet.ncols
        except AttributeError:
            return None

    def gate_voltage(self, index=None):
        """ Called to get the gate voltage for the measurement

        Parameters
        ----------
        index : int
            this allows for accessing of a single item of the voltage
            array without having to loop. for example:
                self.gate_voltage(0) would give the first voltage value
            default value is none, in this case it will return the 
            entire array of current
        """
        voltage = []
        # check that the data exists, if not return None
        if self.__cols() != None:
            # find the column that contains 'GateV'
            for i in range( self.__cols() ):
                if self.data_sheet.cell_value( 0, i ) == "GateV":
                    col = i
            # if a specific index is not given then return all the 
            # voltage values as an array
            if index == None:
                # start at 1 because row 0 in the sheet holds 
                # the headers
                for row in range( 1, self.__rows() ):
                    voltage.append( self.data_sheet.cell_value( row, col ) )
                return voltage
            # if a specific index is given
            elif type(index) == int:
                if index >= 0 and index <= self.__rows():
                    # index + 1 beacuse the first row of the sheet
                    # is the column headers. When reading data the 
                    # value will actually be row + 1 of the index
                    return self.data_sheet.cell_value( index + 1, col )
                # reverse index the array
                # e.g. array[-1] = last item, array[-2] = second last item
                elif index < 0:
                    return self.data_sheet.cell_value( self.__rows() + index, col )
                # index is out of bounds
                else:
                    print "Index is out of bounds"
                    return None
            # if index is not None and also not an int
            else:
                return None
        # sheet does not exist
        else:
            return None

    def max_gate_voltage(self):
        """ Called to get the max gate voltage for the measurement
        """
        try:
            return self.gate_voltage()[-1]
        except TypeError:
            return None

    def min_gate_voltage(self):
        """ Called to get the min gate voltage for the measurement
        """
        try:
            return self.gate_voltage()[0]
        except TypeError:
            return None

    def current(self, index=None, units="A"):
        """ Called to get the current values for the measurement in Amps

        Parameters
        ----------
        index : int or None
            this allows for accessing of a single item of the current
            array without having to loop. for example:
                self.current(0) would give the first current value
            default value is none, in this case it will return the 
            entire array of current
        units : string
            the units to which the current should be converted to 
            1) "A" = Amperes
            2) "nA" = nanoAmperes
            3) "uA" = microAmperes
            4) "mA" = milliAmperes
        """
        current = [] 
        # tuple of units and corresponding multiplication factor
        suffix = ( ('A',1.0), ('nA',1e9), ('uA',1e6), ('mA',1e3) ) 
        # compare the units factor to the units argument and set
        # the multiplaction factor
        for pair in range( len(suffix) ):
            # compare units argument to the tuple pairs' first 
            # argument
            if units == suffix[pair][0]:
                # set the multiplication factor to the tuple pairs'
                # second argument
                factor = suffix[pair][1]
        # check that the data exists, if not return None
        if self.__cols() != None: 
            # find the column that contains the DrainI 
            for i in range( self.__cols() ):
                if self.data_sheet.cell_value( 0, i ) == "DrainI":
                    col = i
            # if a specific index is not given then return all the 
            # current values as an array
            if index == None:
                # start at 1 because row 0 in the sheet holds 
                # the headers
                for row in range( 1, self.__rows() ):
                    current.append( self.data_sheet.cell_value( row, col ) * factor )
                return current
            # if a specific index is given
            elif type(index) == int:
                if index >= 0 and index <= self.__rows():
                    # index + 1 beacuse the first row of the sheet
                    # is the column headers. When reading data the 
                    # value will actually be row + 1 of the index
                    return self.data_sheet.cell_value( index + 1, col ) * factor
                # reverse index the array
                # e.g. array[-1] = last item, array[-2] = second last item
                elif index < 0:
                    return self.data_sheet.cell_value( self.__rows() + index, col ) * factor
                # index is out of bounds
                else:
                    print "Index is out of bounds"
                    return None
            # if index is not None and also not an int
            else:
                return None
        # no data sheet exists
        else:
            return None

    def lnT_current(self, index=None, order=1.5):
        """ Called to get the current at each gate voltage value in the form 
        of Ln( I / T^(order) )

        Parameters
        ----------
        index : int or None
            this allows for accessing of a single item of the lnT_current
            array without having to loop. for example:
                self.lnT_current(0) would give the first lnT_current value
            default value is none, in this case it will return the 
            entire array of lnT_current 
        order : float
            order to which the temperature should be taken. default value 
            is 3/2. Other possible value is 2.0
        """
        # check for correct measurement type
        if self.test_name() == 'vgs-id':
            lnT = [] 
            # if a specific index is not given then return all the 
            # lnT_current values as an array
            if index == None:
                # To check whether it is n-type or p-type, we use the 
                # last current value. (if > 0 then p-type, and 
                # if < 0 then n-type)
                # n-type device, and we should make any negative value
                # equal to zero so as not to cause NaN in log values
                if self.current(-1) > 0:
                    for i in range( len( self.current() ) ):
                        # current is real, calculate lnT
                        if self.current(i) > 0:
                            lnT.append( np.log( self.current(i) /
                                ( scc.k * self.temperature() ** order ) ) )
                        # current is not real, skip it
                        elif self.current(i) <= 0:
                            lnT.append( 0.0 )
                # p-type device, and we should take the absolute value
                # of the current values in order to take log of the 
                # current values.
                # In this case, if the current is negative then it is 
                # considered a 'real' current and should be used, if the
                # current is positive, then it is an 'artifact' and 
                # should not be considered. This elif also checks this.
                elif self.current(-1) < 0:
                    for i in range( len( self.current() ) ):
                        # current is real, calculate lnT
                        if self.current(i) < 0:
                            lnT.append( np.log( abs( self.current(i) ) / 
                                ( scc.k * self.temperature() ** order ) ) )
                        # current is not real, skip it
                        elif self.current(i) >= 0:
                            lnT.append( 0.0 )
                return lnT
            # index is given as integer
            elif type(index) == int:
                # index + 1 beacuse the first row of the sheet
                # is the column headers. When reading data the 
                # value will actually be row + 1 of the index
                curr = self.current( index ) 
                return np.log( self.current(index) / 
                        ( scc.k * self.temperature() ** order ) ) 
            # index error, it is not int or None type
            else:
                return None
        # not correct measurement type
        else: 
            return None

    def abs_current(self, index=None):
        """ Called to get the absolute value of the current values 
        Amps

        Parameters
        ----------
        index : int or None
        """
        # check measurement type
        if self.test_name() == 'vgs-id':
            abs_current = []
            # no index given, return entire array
            if index == None:
                for i in range( len( self.current() ) ):
                    abs_current.append( self.current(i) )
                return abs_current
            # index is given, return single value
            elif type(index) == int:
                return abs( self.current(index) )
        # wrong measurement type
        else:
            return None 

    def abs_normalized_current(self, index=None):
        """ Called to get the absolute value of the current divided by
        the width of the channel
        
        Parameters
        ----------
        index : int or None
        """
        # check measurement type
        if self.test_name() == 'vgs-id':
            abs_norm_current = []
            # no index given, return entire array
            if index == None:
                for i in range( len( self.current() ) ):
                    abs_norm_current.append( abs(self.current(i))/self.width)
                return abs_norm_current
            # index is given, return single value
            elif type(index) == int:
                return abs(self.current(index))/self.width
        # wrong measurement type
        else:
            return None 

    def normalized_current(self, index=None):
        """ Called to get the current divided by the width of the 
        channel

        Parameters
        ----------
        index : int or None
        """
        # check for measurement type
        if self.test_name() == 'vgs-id':
            norm_current = []
            # no index given, return entire array
            if index == None:
                for i in range( len( self.current() ) ):
                    norm_current.append( self.current(i)/self.width )
                return norm_current
            # index is given, return single value
            elif type(index) == int:
                return self.current(index)/self.width
        # wrong measurement type
        else:
            return None 

    def conductivity(self, index=None):
        """ Called to get the conductivity in uS, where
        S = I/Vds * L/W

        Parameters
        ----------
        index : int or None
        """
        # check for correct measurement type
        if self.test_name() == "vgs-id":
            conduct = []
            # no index given, return entire array
            if index == None:
                for i in range( len( self.current() ) ):
                    # current in microAmps, use units arg
                    val = self.current(index=i, units='uA')
                    val = ( val / self.drain_voltage() ) * ( self.length / self.width )
                    conduct.append( val )
                return conduct
            # index given, return single value
            elif type(index) == int:
                val = self.current(index=index, units='uA')
                val = ( val/self.drain_voltage() ) * ( self.length / self.width )
                return val
        # wrong measurement type
        else:
            return None
    
    def __set_plot_params(self):
        """ Called from plotting functions to reset the parameters
        of matplotlib to default
        """
        mpl.rcParams.update(mpl.rcParamsDefault)

    def plot_transfer(self, axis_type, save_name=""):
        """ Called to plot the transfer curve for a data set

        Parameters
        ----------
        axis_type : string
            denotes whether the plot should semilogy or linear
            options are axis_type="log" or axis_type="linear"
        save_name : string
            denotes the name for which the plot should be save as pdf
            to, default to empty string and it will not save the plot
            in this case, rather it will just call plt.show()
        """
        # check for correct measurement type
        if self.test_name() == "vgs-id":
            # check to make sure current has values
            if self.current() and self.gate_voltage() is not None:
                # set plot parameters to default
                self.__set_plot_params()
                # x-label will always be gate voltage
                plt.xlabel(r"$V_{gs}\,(\mathrm{V})$", fontsize=14)
                # if it is logY plot, current will be in amps
                if axis_type == "log":
                    plt.ylabel(r"$I_{ds}\,(\mathrm{A})$", fontsize=14)
                    plt.semilogy(self.gate_voltage(), self.current())
                # if it is a linear plot, current will be in microAmps
                elif axis_type == "linear":
                    plt.ylabel(r"$I_{ds}\,(\mu\mathrm{A})$", fontsize=14)
                    plt.plot(self.gate_voltage(), self.current(units="uA"))
                else:
                    print "Invalid axis type"
                plt.tight_layout()
                if save_name == "":
                    plt.show()
                else:
                    plt.savefig(save_name+".pdf")
            else:
                return None
        # wrong measurement type
        else:
            return None

    def plot_normalized_transfer(self):
        pass
    
    def plot_conductivity(self, save_name=""):
        """ Called to plot the transfer curve for a data set

        Parameters
        ----------
        axis_type : string
            denotes whether the plot should semilogy or linear
            options are axis_type="log" or axis_type="linear"
        save_name : string
            denotes the name for which the plot should be save as pdf
            to, default to empty string and it will not save the plot
            in this case, rather it will just call plt.show()
        """
        # check for correct measurement type
        if self.test_name() == 'vgs-id':
            # check to make sure current has values
            if self.current() and self.gate_voltage() is not None:
                # set plot parameters to default
                self.__set_plot_params()
                # x-label will always be gate voltage
                plt.xlabel(r"$V_{gs}\,(\mathrm{V})$", fontsize=14)
                plt.ylabel(r"$\sigma_{2D}\,(\mu\mathrm{S})$", fontsize=14)
                plt.plot(self.gate_voltage(), self.conductivity())
                plt.tight_layout()
                if save_name == "":
                    plt.show()
                else:
                    plt.savefig(save_name+".pdf")
            else:
                return None   
        # wrong measurement type
        else:
            return None
    
class SBH(Measurement):
    def __init__(self, *files):
        self.filenames = files
        #print files[0][0].gate_voltage()
    
    def __voltage_headers(self, order="3/2"):
        """ Called to make the voltage headers for the SBH data 

        Parameters
        ----------
        order : string
            order of ln( I / (kb * T^(order) ) ) 
            defaults to 3/2, other value could be 2
        """
        header = []
        base_str = "I @ Vgs = "
        lnT_base_str = "ln(I/(kb*T^("+str(order)+"))) @ Vgs = "
        # loop only over a single measurement here because it is assumed 
        # that the step size is consistent throughout all the measurements
        # if it is not the case, then it will not work
        for i in range( 0, len( self.filenames[0][0].gate_voltage() ) ):
            voltage = self.filenames[0][0].gate_voltage()[i]
            voltage = str( round(voltage, 2) ) + " V"
            header.append(base_str + voltage)
            header.append(lnT_base_str + voltage)
        return header

    def __current_voltage_dict(self, order=1.5):
        """Called to make the current and voltage dictionary, calls upon the
        __voltage_headers function to combine

        Parameters
        ----------
        order : float
            order of T^(order), defaults to 3/2, also could be 2
        """
        currents = [ [] for i in range( len(self.filenames[0][0].current()) * 2 ) ]
        # loop over class args passed
        for i in range( 0, len( self.filenames[0] ) ):
            # current files measurement temperature
            curr_temp = self.filenames[0][i].temperature()
            print curr_temp
            # loop over each current value in each file
            for j in range( 0, len( self.filenames[0][i].current() ) ):
                # current values at each gate voltage
                curr_val = self.filenames[0][i].current()[j] 
                # ln( I/ (kb * T^(3/2) ) ) values at each gate voltage
                try:
                    lnT_curr_val = np.log( curr_val / (scc.k * curr_temp**(order)))
                except RuntimeWarning:
                    lnT_curr_val = 0.0
                #
                currents[j*2-2].append( curr_val )
                currents[j*2-1].append( lnT_curr_val )
        return OrderedDict( zip( self.__voltage_headers(), currents ) )
    
        
    def __temperature_dict(self)  :
        """ Called to make the temperature dictionary for SBH analysis
        """
        # each column header
        headers = ['T (K)', '1/kT', '1000/T (1/K)']
        # each column has its own list of values
        temps = [ [] for head in range( len( headers) ) ]
        # loop over each class argument
        for t in range ( len( self.filenames[0] ) ):
            # get the temperature of current argument 
            curr_t = self.filenames[0][t].temperature()
            temps[0].append( curr_t )
            temps[1].append( scc.e / (scc.k * curr_t) )
            temps[2].append( 1000.0 / curr_t)
        # combine headers and temps into a list and make ordered dict
        return OrderedDict( zip( headers, temps ) )
            
    def __merge_dicts(*dict_args):
        """ Given any number of dicts, shallow copy and merge into a new
        dicts, precedence goes to key value pairs in latter dicts

        Parameters
        ----------
        *dict_args : dictionary or dictionaries 
            pass any number of dictionaries to be merged
            e.x. merge_dicts( a, b, c, d, ..., z )
        """
        # use ordered dictionaries to preserve key, value order
        result = OrderedDict()
        for dictionary in dict_args:
            result.update( dictionary )
        return result
    