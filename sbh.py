from measurement import Measurement
from collections import OrderedDict
import xlrd
import xlwt
import scipy.constants as scc
import numpy as np 

class SBH:
    def __init__(self, Measurements, order=1.5):
        # list of measurements instantiated from the
        # Measurement class
        self.measurements = Measurements    
        self.order = order
        # assume the list is not sorted by temperature and does so
        # doing this in the constructor ensures it is always sorted
        self.__sort_by_temperature()

    def __repr__(self):
        for i in range( len( self.measurements ) ):
            print "[", i, "] = ", self.measurements[i]
        
    def __str__(self):
        return self.__repr__()

    def get_num_measurements(self):
        """ Called check the number of measurements 
        contained in self.measurements
        """
        return len( self.measurements )   

    def add_measurement(self, item):
        """ Called to add a measurement to the 
        list of existing measurements

        Parameters
        ----------
        item : Measurement
        """
        self.measurements.append(item)

    def remove_measurement(self, index=None):
        """ Called to remove a measurement from the
        list of measurements

        Parameters
        ----------
        index : int or None
            index of the measurement to be removed,
            if it is None, then the default is to remove
            the last item
        """ 
        if index is not None:
            return self.measurements.pop(index)
        else:
            return self.measurements.pop()

    def __sort_by_temperature(self):
        """ Called to sort the list of measurements by temperature
        in descending order
        """
        temps = [] 
        # first get each temperature
        for i in range( len( self.measurements ) ):
            temps.append( self.measurements[i].temperature() )
        # reverse sort (descending order)
        self.measurements = [x for _, x in sorted(zip(temps, self.measurements), key=lambda pair: pair[0], reverse=True)]

    def get_temperatures(self):
        """ Called to return an array of all the temperatures
        in self.measurements
        """
        temps = []
        for i in range( len( self.measurements ) ):
            temps.append( self.measurements[i].temperature() )
        return temps
    
    def lnT_current(self, index):
        """ Called to return the whole lnT array for a given
        measurement

        Parameters
        ----------
        index : int 

        order : float
            order of the exponent in Ln(I/T^(order)), usually either 1.5 or 2.0
        """
        try:
            return self.measurements[index].lnT_current(order=self.order)
        except IndexError:
            print "Index out of Bounds, Measurement index does not exist"
            return None
    
    def __check_gate_step_consistency(self):
        """ Called to check that the gate step size is the same throughout all the 
        measurements in self.measurements, if it is not it will return false and
        the further analysis cannot be completed
        """
        steps = [] 
        for i in range( len( self.measurements ) ):
            # get the steps of each measurement, round for sake of equality checks
            steps.append( round(self.measurements[i].gate_voltage()[1] - self.measurements[i].gate_voltage()[0], 2) )
        # compare all steps to make sure they are equal
        if all( x == steps[0] for x in steps ):
            return True
        else:
            return False
    
    def generate_output_headers(self):
        """ Called to generate an array of headers for each voltage column
        """
        # check that step sizes are equal
        if self.__check_gate_step_consistency() == True:
            base = "I @ Vgs = " 
            lnT_base = "Ln(I/T^("+str(self.order)+")) @ Vgs = "
            heads = []
            # loop over the first dimension of heads, e.g. len(heads)
            for i in range( len( self.measurements[0].gate_voltage() ) ):
                # round for readability
                val = round( self.measurements[0].gate_voltage()[i], 2 )
                heads.append( base + str(val) + "V" )
                heads.append( lnT_base + str(val) + "V" )
            return heads
        else:
            print "Gate step size is not equal"
            return None

    def lnT_current_dict(self):
        pass 
    
    def temperature_dict(self):
        headers = ["T (K)", "1/kbT (1/eV)", "1000/T (1/K)"]
        
    
    def merge_dicts(self, *dict_args):
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