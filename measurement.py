import xlrd
import xlwt
import scipy.constants as sc
import numpy as np 
import matplotlib.pyplot as plt
import math
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

    Basic usage, assuming filename 'test.xls'
    >>> x = Measurement('test.xls')
    >>> x.current() # prints all the currents
    >>> x.write_analysis() # write all analysis to file
    """
    def __init__(self, filename, width=1.0, length=1.0, capacitance=1.0):
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
        # length in micrometers
        self.width = width 
        # length in micrometers 
        self.length = length
        # capacitance in F/cm^2
        self.capacitance = capacitance 
    
    def width(self):
        """ Called to get the width of the device 
        """
        return self.width

    def length(self):
        """ Called to get the length of the device
        """
        return self.length

    def write_analysis(self):
        """ Called to write the measurement data and some data 
        analysis to an excel file
        """
        # get the current workbook and the data sheet
        # self.data_sheet cannot be used, because that references the 
        # place in memory but not the actual sheet
        wb = xlrd.open_workbook(self.filename)
        # data sheet 
        sheet = wb.sheet_by_index(0)
        if self.test_name() == 'vgs-id':
            # initalize a 2D array to store all the data that will 
            # be copied over
            data = [ [] for col in range( self.__cols() ) ]
            # get each row and column of the initial data from 
            # the measurement
            for col in range( self.__cols() ):
                # self.__rows() works here because we want to use the 
                # total number of rows in the sheet including the headers
                for row in range( self.__rows() ):
                    data[col].append( sheet.cell_value( row, col ) )
            # headers of analyzed data
            new_headers = ["S (uS) "+str(self.drain_voltage())
                +"V "+str(self.temperature())+"K", "Norm Ids (A/um) "+
                str(self.drain_voltage())+"V "+str(self.temperature() )+
                "K"]
            # analyzed data to be added to the sheet
            new_data = [ [] for col in range( len( new_headers ) ) ]
            # populate new_data with conductivity and the norm current
            for col in range( len( new_headers ) ):
                new_data[col].append( new_headers[col] )
                if col == 0:
                    # use len( self.conductivity() ) because 
                    # self.__rows() = self.conductivity() + 1
                    # self.__rows() includes the length with the original header
                    # included, so self.__rows() would throw an index error
                    for row in range( len( self.conductivity() ) ):
                        new_data[col].append( self.conductivity( row ) )
                elif col == 1:
                    # use len( self.normalized_current() ) because 
                    # self.__rows() = self.normalized_current() + 1
                    # self.__rows() includes the length with the original header
                    # included, so self.__rows() would throw an index error
                    for row in range( len(self.normalized_current() ) ):
                        new_data[col].append( self.normalized_current( row ) )
            # clean up the microamps drain current header to include
            # drain voltage and temperature
            self.__replace_header(data, "IDS_UA", "Ids (uA) "+str(self.drain_voltage())
                +"V "+str(self.temperature())+"K" )
            # clean up the abs ids current header to include 
            # drain voltage and temperature
            self.__replace_header(data, "ABS_IDS", "ABS Ids (A) "+str(self.drain_voltage())
                +"V "+str(self.temperature())+"K") 
            # concatenate old data with the analyzed data 
            data += new_data
            # initialize new workbook for writing
            new_book = xlwt.Workbook()
            # add sheet
            new_sheet = new_book.add_sheet("Analyzed Data")
            print len(data), len(data[0])
            # number of columns is len(data)
            for col in range( len( data ) ):
                # number of rows is len(data[0]) because the array
                # is not jagged
                for row in range( len( data[0] ) ):
                    new_sheet.write( row, col, data[col][row] )
            # save the book with a file name that is the same as 
            # self.file name with an 'analyzed' added
            new_book.save(self.__strip_excel()+"_analyzed.xls")
    
    def __strip_excel(self):
        """ Called to strip the .xls extension from self.filename
        """
        return self.filename[:-4]

    def __replace_header(self, array, old_str, replace_str):
        for col in range( len(array) ):
            if array[col][0] == old_str:
                array[col][0] = replace_str
        
                
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
        channel in Amps

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
    
    def __get_voltage_val_index(self, val, epsilon=1e-1):
        """ Called to get the index at which voltage array has a 
        particular value. For example, if we want to know at which index 
        self.gate_voltage() has a value of 0.0 this function would be 
        called as:
            self.__get_val_index( self.gate_voltage(), 0.0 )
        Note this is a bit tricky because the gate_voltage does not 
        hit exactly zero

        Parameters
        ----------
        val : float or int
            value that is to be searched for
        """
        start = round(self.min_gate_voltage(), 3)
        stop = round(self.max_gate_voltage() , 3)
        step = self.gate_step_size()
        # index to be returned
        index = 0
        while start <= stop:
            # check for convergence
            if abs(start - val) < epsilon:
                return index
            # if not converged then update
            else:
                start += step
                index += 1
    
    def reliability_factor(self, mu_linear):
        """ Called to get the reliability factor where
        r_lin = ((|I_ds^max| - |I_ds^0|)/|V_gs^max|)
                ------------------------------------
                ((|V_ds| * W * C * mu_linear) / L)
        where 
            |I_ds^max| = abs value of max current 
            |I_ds^0| = abs value of current at V_gs = 0 V
            |V_gs^max| = abs value of max gate voltage
            |V_ds| = abs value of drain voltage
            W = device width
            L = device length
            C = gate capacitance 
            mu_linear = estimated linear mobility
        returns a tuple of r_lin and mu_eff where 
            mu_eff = r_lin * mu_linear
        
        Parameters
        ----------
        mu_linear : float
            estimate linear mobility, found from linear fit
        """
        current_max = abs(self.current(-1))
        current_0 = abs(self.current(self.__get_voltage_val_index(0.0)))
        print current_0
        gate_max = abs(self.gate_voltage(-1))
        numer = (current_max - current_0)/gate_max
        denom = (self.drain_voltage()*self.width*self.capacitance*mu_linear)/self.length
        r_lin = numer/denom 
        mu_eff = r_lin * mu_linear
        return (r_lin, mu_eff)



    def __set_plot_params(self):
        """ Called from plotting functions to reset the parameters
        of matplotlib to default
        """
        mpl.rcParams.update(mpl.rcParamsDefault)

    def plot_transfer(self, axis, save_name=""):
        """ Called to plot the transfer curve for a data set

        Parameters
        ----------
        axis : string
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
                if axis == "log":
                    plt.ylabel(r"$I_{ds}\,(\mathrm{A})$", fontsize=14)
                    plt.semilogy(self.gate_voltage(), self.current())
                # if it is a linear plot, current will be in microAmps
                elif axis == "linear":
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

    def plot_normalized_transfer(self, save_name=""):
        """ Called to plot the normalized transfer curve for a data set

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
                plt.ylabel(r"$I_{ds}/W\,(\mathrm{A}/\mu\mathrm{m})$", fontsize=14)
                plt.semilogy(self.gate_voltage(), self.normalized_current())
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
    