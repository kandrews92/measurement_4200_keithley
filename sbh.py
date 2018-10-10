from measurement import Measurement
import xlrd
import xlwt
import scipy.constants as scc
import numpy as np 

class SBH:
    def __init__(self, Measurements):
        # list of measurements instantiated from the
        # Measurement class
        self.measurements = Measurements    
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
    
    def lnT_current(self, index, order=1.5):
        """ Called to return the whole conductivity array for a given
        measurement

        Parameters
        ----------
        index : int 

        order : float
            order of the exponent in Ln(I/T^(order)), usually either 1.5 or 2.0
        """
        try:
            return self.measurements[index].lnT_current()
        except IndexError:
            print "Index out of Bounds, Measurement index does not exist"
            return None
    
    def generate_output_headers(self):
        pass