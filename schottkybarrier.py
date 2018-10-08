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
    