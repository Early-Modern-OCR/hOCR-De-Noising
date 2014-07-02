# -*- coding: utf-8 -*-
#import sys
#Add search path to 

#sys.path.append('/home/anshulg/PythonPackages/lib/python')

import bs4
import numpy as np;
#import matplotlib.pyplot as pl
#import peaks_find as pks
import optparse as parser_opt
import datetime
import time
from math import pi, log
from scipy import fft, ifft
from scipy.optimize import curve_fit
#from memory_profiler import profile

#@profile    
def deNoise(filePath,fileName,debugFlag):
    def _datacheck_peakdetect(x_axis, y_axis):
        if x_axis is None:
            x_axis = range(len(y_axis))    
        if len(y_axis) != len(x_axis):
            raise (ValueError,'Input vectors y_axis and x_axis must have same length')
    
        #needs to be a numpy array
        y_axis = np.array(y_axis)
        x_axis = np.array(x_axis)
        return x_axis, y_axis
    
    def _peakdetect_parabole_fitter(raw_peaks, x_axis, y_axis, points):
        """
        Performs the actual parabole fitting for the peakdetect_parabole function.
        
        keyword arguments:
        raw_peaks -- A list of either the maximium or the minimum peaks, as given
            by the peakdetect_zero_crossing function, with index used as x-axis
        x_axis -- A numpy list of all the x values
        y_axis -- A numpy list of all the y values
        points -- How many points around the peak should be used during curve
            fitting, must be odd.
        
        return -- A list giving all the peaks and the fitted waveform, format:
            [[x, y, [fitted_x, fitted_y]]]
            
        """
        func = lambda x, k, tau, m: k * ((x - tau) ** 2) + m
        fitted_peaks = []
        for peak in raw_peaks:
            index = peak[0]
            x_data = x_axis[index - points // 2: index + points // 2 + 1]
            y_data = y_axis[index - points // 2: index + points // 2 + 1]
            # get a first approximation of tau (peak position in time)
            tau = x_axis[index]
            # get a first approximation of peak amplitude
            m = peak[1]
            
            # build list of approximations
            # k = -m as first approximation?
            p0 = (-m, tau, m)
            popt, pcov = curve_fit(func, x_data, y_data, p0)
            # retrieve tau and m i.e x and y value of peak
            x, y = popt[1:3]
            
            # create a high resolution data set for the fitted waveform
            x2 = np.linspace(x_data[0], x_data[-1], points * 10)
            y2 = func(x2, *popt)
            
            fitted_peaks.append([x, y, [x2, y2]])
            
        return fitted_peaks
        
        
    def peakdetect(y_axis, x_axis = None, lookahead = 300, delta=0):
        """
        Converted from/based on a MATLAB script at: 
        http://billauer.co.il/peakdet.html
        
        function for detecting local maximas and minmias in a signal.
        Discovers peaks by searching for values which are surrounded by lower
        or larger values for maximas and minimas respectively
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- (optional) A x-axis whose values correspond to the y_axis list
            and is used in the return to specify the postion of the peaks. If
            omitted an index of the y_axis is used. (default: None)
        lookahead -- (optional) distance to look ahead from a peak candidate to
            determine if it is the actual peak (default: 200) 
            '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
        delta -- (optional) this specifies a minimum difference between a peak and
            the following points, before a peak may be considered a peak. Useful
            to hinder the function from picking up false peaks towards to end of
            the signal. To work well delta should be set to delta >= RMSnoise * 5.
            (default: 0)
                delta function causes a 20% decrease in speed, when omitted
                Correctly used it can double the speed of the function
        
        return -- two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a tupple
            of: (position, peak_value) 
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do: 
            x, y = zip(*tab)
        """
        max_peaks = []
        min_peaks = []
        dump = []   #Used to pop the first hit which almost always is false
           
        # check input data
        x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
        # store data length for later use
        length = len(y_axis)
        
        
        #perform some checks
        if lookahead < 1:
            raise ValueError, "Lookahead must be '1' or above in value"
        if not (np.isscalar(delta) and delta >= 0):
            raise ValueError, "delta must be a positive number"
        
        #maxima and minima candidates are temporarily stored in
        #mx and mn respectively
        mn, mx = np.Inf, -np.Inf
        
        #Only detect peak if there is 'lookahead' amount of points after it
        for index, (x, y) in enumerate(zip(x_axis[:-lookahead], 
                                            y_axis[:-lookahead])):
            if y > mx:
                mx = y
                mxpos = x
            if y < mn:
                mn = y
                mnpos = x
            
            ####look for max####
            if y < mx-delta and mx != np.Inf:
                #Maxima peak candidate found
                #look ahead in signal to ensure that this is a peak and not jitter
                if y_axis[index:index+lookahead].max() < mx:
                    max_peaks.append([mxpos, mx])
                    dump.append(True)
                    #set algorithm to only find minima now
                    mx = np.Inf
                    mn = np.Inf
                    if index+lookahead >= length:
                        #end is within lookahead no more peaks can be found
                        break
                    continue
                #else:  #slows shit down this does
                #    mx = ahead
                #    mxpos = x_axis[np.where(y_axis[index:index+lookahead]==mx)]
            
            ####look for min####
            if y > mn+delta and mn != -np.Inf:
                #Minima peak candidate found 
                #look ahead in signal to ensure that this is a peak and not jitter
                if y_axis[index:index+lookahead].min() > mn:
                    min_peaks.append([mnpos, mn])
                    dump.append(False)
                    #set algorithm to only find maxima now
                    mn = -np.Inf
                    mx = -np.Inf
                    if index+lookahead >= length:
                        #end is within lookahead no more peaks can be found
                        break
                #else:  #slows shit down this does
                #    mn = ahead
                #    mnpos = x_axis[np.where(y_axis[index:index+lookahead]==mn)]
        
        
        #Remove the false hit on the first value of the y_axis
        try:
            if dump[0]:
                max_peaks.pop(0)
            else:
                min_peaks.pop(0)
            del dump
        except IndexError:
            #no peaks were found, should the function return empty lists?
            pass
            
        return [max_peaks, min_peaks]
        
        
    def peakdetect_fft(y_axis, x_axis, pad_len = 5):
        """
        Performs a FFT calculation on the data and zero-pads the results to
        increase the time domain resolution after performing the inverse fft and
        send the data to the 'peakdetect' function for peak 
        detection.
        
        Omitting the x_axis is forbidden as it would make the resulting x_axis
        value silly if it was returned as the index 50.234 or similar.
        
        Will find at least 1 less peak then the 'peakdetect_zero_crossing'
        function, but should result in a more precise value of the peak as
        resolution has been increased. Some peaks are lost in an attempt to
        minimize spectral leakage by calculating the fft between two zero
        crossings for n amount of signal periods.
        
        The biggest time eater in this function is the ifft and thereafter it's
        the 'peakdetect' function which takes only half the time of the ifft.
        Speed improvementd could include to check if 2**n points could be used for
        fft and ifft or change the 'peakdetect' to the 'peakdetect_zero_crossing',
        which is maybe 10 times faster than 'peakdetct'. The pro of 'peakdetect'
        is that it resutls in one less lost peak. It should also be noted that the
        time used by the ifft function can change greatly depending on the input.
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- A x-axis whose values correspond to the y_axis list and is used
            in the return to specify the postion of the peaks.
        pad_len -- (optional) By how many times the time resolution should be
            increased by, e.g. 1 doubles the resolution. The amount is rounded up
            to the nearest 2 ** n amount (default: 5)
        
        return -- two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a tupple
            of: (position, peak_value) 
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do: 
            x, y = zip(*tab)
        """
        # check input data
        x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
        zero_indices = zero_crossings(y_axis, window = 11)
        #select a n amount of periods
        last_indice = - 1 - (1 - len(zero_indices) & 1)
        # Calculate the fft between the first and last zero crossing
        # this method could be ignored if the begining and the end of the signal
        # are discardable as any errors induced from not using whole periods
        # should mainly manifest in the beginning and the end of the signal, but
        # not in the rest of the signal
        fft_data = fft(y_axis[zero_indices[0]:zero_indices[last_indice]])
        padd = lambda x, c: x[:len(x) // 2] + [0] * c + x[len(x) // 2:]
        n = lambda x: int(log(x)/log(2)) + 1
        # padds to 2**n amount of samples
        fft_padded = padd(list(fft_data), 2 ** 
                    n(len(fft_data) * pad_len) - len(fft_data))
        
        # There is amplitude decrease directly proportional to the sample increase
        sf = len(fft_padded) / float(len(fft_data))
        # There might be a leakage giving the result an imaginary component
        # Return only the real component
        y_axis_ifft = ifft(fft_padded).real * sf #(pad_len + 1)
        x_axis_ifft = np.linspace(
                    x_axis[zero_indices[0]], x_axis[zero_indices[last_indice]],
                    len(y_axis_ifft))
        # get the peaks to the interpolated waveform
        max_peaks, min_peaks = peakdetect(y_axis_ifft, x_axis_ifft, 500,
                                        delta = abs(np.diff(y_axis).max() * 2))
        #max_peaks, min_peaks = peakdetect_zero_crossing(y_axis_ifft, x_axis_ifft)
        
        # store one 20th of a period as waveform data
        data_len = int(np.diff(zero_indices).mean()) / 10
        data_len += 1 - data_len & 1
        
        
        fitted_wave = []
        for peaks in [max_peaks, min_peaks]:
            peak_fit_tmp = []
            index = 0
            for peak in peaks:
                index = np.where(x_axis_ifft[index:]==peak[0])[0][0] + index
                x_fit_lim = x_axis_ifft[index - data_len // 2:
                                        index + data_len // 2 + 1]
                y_fit_lim = y_axis_ifft[index - data_len // 2:
                                        index + data_len // 2 + 1]
                
                peak_fit_tmp.append([x_fit_lim, y_fit_lim])
            fitted_wave.append(peak_fit_tmp)
        
        #pylab.plot(range(len(fft_data)), fft_data)
        #pylab.show()
        
        #pylab.plot(x_axis, y_axis)
       # pylab.hold(True)
       # pylab.plot(x_axis_ifft, y_axis_ifft)
        #for max_p in max_peaks:
        #    pylab.plot(max_p[0], max_p[1], 'xr')
        #pylab.show()
        return [max_peaks, min_peaks]
        
        
    def peakdetect_parabole(y_axis, x_axis, points = 9):
        """
        Function for detecting local maximas and minmias in a signal.
        Discovers peaks by fitting the model function: y = k (x - tau) ** 2 + m
        to the peaks. The amount of points used in the fitting is set by the
        points argument.
        
        Omitting the x_axis is forbidden as it would make the resulting x_axis
        value silly if it was returned as index 50.234 or similar.
        
        will find the same amount of peaks as the 'peakdetect_zero_crossing'
        function, but might result in a more precise value of the peak.
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- A x-axis whose values correspond to the y_axis list and is used
            in the return to specify the postion of the peaks.
        points -- (optional) How many points around the peak should be used during
            curve fitting, must be odd (default: 9)
        
        return -- two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a list
            of: (position, peak_value) 
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do: 
            x, y = zip(*max_peaks)
        """
        # check input data
        x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
        # make the points argument odd
        points += 1 - points % 2
        #points += 1 - int(points) & 1 slower when int conversion needed
        
        # get raw peaks
        max_raw, min_raw = peakdetect_zero_crossing(y_axis)
        
        # define output variable
        max_peaks = []
        min_peaks = []
        
        max_ = _peakdetect_parabole_fitter(max_raw, x_axis, y_axis, points)
        min_ = _peakdetect_parabole_fitter(min_raw, x_axis, y_axis, points)
        
        max_peaks = map(lambda x: [x[0], x[1]], max_)
        max_fitted = map(lambda x: x[-1], max_)
        min_peaks = map(lambda x: [x[0], x[1]], min_)
        min_fitted = map(lambda x: x[-1], min_)
        
        
        #pylab.plot(x_axis, y_axis)
        #pylab.hold(True)
        #for max_p, max_f in zip(max_peaks, max_fitted):
        #    pylab.plot(max_p[0], max_p[1], 'x')
        #    pylab.plot(max_f[0], max_f[1], 'o', markersize = 2)
        #for min_p, min_f in zip(min_peaks, min_fitted):
        #    pylab.plot(min_p[0], min_p[1], 'x')
        #    pylab.plot(min_f[0], min_f[1], 'o', markersize = 2)
        #pylab.show()
        
        return [max_peaks, min_peaks]
        
     
    def peakdetect_sine(y_axis, x_axis, points = 9, lock_frequency = False):
        """
        Function for detecting local maximas and minmias in a signal.
        Discovers peaks by fitting the model function:
        y = A * sin(2 * pi * f * x - tau) to the peaks. The amount of points used
        in the fitting is set by the points argument.
        
        Omitting the x_axis is forbidden as it would make the resulting x_axis
        value silly if it was returned as index 50.234 or similar.
        
        will find the same amount of peaks as the 'peakdetect_zero_crossing'
        function, but might result in a more precise value of the peak.
        
        The function might have some problems if the sine wave has a
        non-negligible total angle i.e. a k*x component, as this messes with the
        internal offset calculation of the peaks, might be fixed by fitting a 
        k * x + m function to the peaks for offset calculation.
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- A x-axis whose values correspond to the y_axis list and is used
            in the return to specify the postion of the peaks.
        points -- (optional) How many points around the peak should be used during
            curve fitting, must be odd (default: 9)
        lock_frequency -- (optional) Specifies if the frequency argument of the
            model function should be locked to the value calculated from the raw
            peaks or if optimization process may tinker with it. (default: False)
        
        return -- two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a tupple
            of: (position, peak_value) 
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do: 
            x, y = zip(*tab)
        """
        # check input data
        x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
        # make the points argument odd
        points += 1 - points % 2
        #points += 1 - int(points) & 1 slower when int conversion needed
        
        # get raw peaks
        max_raw, min_raw = peakdetect_zero_crossing(y_axis)
        
        # define output variable
        max_peaks = []
        min_peaks = []
        
        # get global offset
        offset = np.mean([np.mean(max_raw, 0)[1], np.mean(min_raw, 0)[1]])
        # fitting a k * x + m function to the peaks might be better
        #offset_func = lambda x, k, m: k * x + m
        
        # calculate an approximate frequenzy of the signal
        Hz = []
        for raw in [max_raw, min_raw]:
            if len(raw) > 1:
                peak_pos = [x_axis[index] for index in zip(*raw)[0]]
                Hz.append(np.mean(np.diff(peak_pos)))
        Hz = 1 / np.mean(Hz)
        
        # model function
        # if cosine is used then tau could equal the x position of the peak
        # if sine were to be used then tau would be the first zero crossing
        if lock_frequency:
            func = lambda x, A, tau: A * np.sin(2 * pi * Hz * (x - tau) + pi / 2)
        else:
            func = lambda x, A, Hz, tau: A * np.sin(2 * pi * Hz * (x - tau) + 
                                                    pi / 2)
        #func = lambda x, A, Hz, tau: A * np.cos(2 * pi * Hz * (x - tau))
        
        
        #get peaks
        fitted_peaks = []
        for raw_peaks in [max_raw, min_raw]:
            peak_data = []
            for peak in raw_peaks:
                index = peak[0]
                x_data = x_axis[index - points // 2: index + points // 2 + 1]
                y_data = y_axis[index - points // 2: index + points // 2 + 1]
                # get a first approximation of tau (peak position in time)
                tau = x_axis[index]
                # get a first approximation of peak amplitude
                A = peak[1]
                
                # build list of approximations
                if lock_frequency:
                    p0 = (A, tau)
                else:
                    p0 = (A, Hz, tau)
                
                # subtract offset from waveshape
                y_data -= offset
                popt, pcov = curve_fit(func, x_data, y_data, p0)
                # retrieve tau and A i.e x and y value of peak
                x = popt[-1]
                y = popt[0]
                
                # create a high resolution data set for the fitted waveform
                x2 = np.linspace(x_data[0], x_data[-1], points * 10)
                y2 = func(x2, *popt)
                
                # add the offset to the results
                y += offset
                y2 += offset
                y_data += offset
                
                peak_data.append([x, y, [x2, y2]])
           
            fitted_peaks.append(peak_data)
        
        # structure date for output
        max_peaks = map(lambda x: [x[0], x[1]], fitted_peaks[0])
        max_fitted = map(lambda x: x[-1], fitted_peaks[0])
        min_peaks = map(lambda x: [x[0], x[1]], fitted_peaks[1])
        min_fitted = map(lambda x: x[-1], fitted_peaks[1])
        
        
        #pylab.plot(x_axis, y_axis)
        #pylab.hold(True)
        #for max_p, max_f in zip(max_peaks, max_fitted):
        #    pylab.plot(max_p[0], max_p[1], 'x')
        #    pylab.plot(max_f[0], max_f[1], 'o', markersize = 2)
        #for min_p, min_f in zip(min_peaks, min_fitted):
        #    pylab.plot(min_p[0], min_p[1], 'x')
        #    pylab.plot(min_f[0], min_f[1], 'o', markersize = 2)
        #pylab.show()
        
        return [max_peaks, min_peaks]
     
        
    def peakdetect_sine_locked(y_axis, x_axis, points = 9):
        """
        Convinience function for calling the 'peakdetect_sine' function with
        the lock_frequency argument as True.
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- A x-axis whose values correspond to the y_axis list and is used
            in the return to specify the postion of the peaks.
        points -- (optional) How many points around the peak should be used during
            curve fitting, must be odd (default: 9)
            
        return -- see 'peakdetect_sine'
        """
        return peakdetect_sine(y_axis, x_axis, points, True)
        
        
    def peakdetect_zero_crossing(y_axis, x_axis = None, window = 11):
        """
        Function for detecting local maximas and minmias in a signal.
        Discovers peaks by dividing the signal into bins and retrieving the
        maximum and minimum value of each the even and odd bins respectively.
        Division into bins is performed by smoothing the curve and finding the
        zero crossings.
        
        Suitable for repeatable signals, where some noise is tolerated. Excecutes
        faster than 'peakdetect', although this function will break if the offset
        of the signal is too large. It should also be noted that the first and
        last peak will probably not be found, as this function only can find peaks
        between the first and last zero crossing.
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- (optional) A x-axis whose values correspond to the y_axis list
            and is used in the return to specify the postion of the peaks. If
            omitted an index of the y_axis is used. (default: None)
        window -- the dimension of the smoothing window; should be an odd integer
            (default: 11)
        
        return -- two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a tupple
            of: (position, peak_value) 
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do: 
            x, y = zip(*tab)
        """
        # check input data
        x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
        
        zero_indices = zero_crossings(y_axis, window = window)
        period_lengths = np.diff(zero_indices)
                
        bins_y = [y_axis[index:index + diff] for index, diff in 
            zip(zero_indices, period_lengths)]
        bins_x = [x_axis[index:index + diff] for index, diff in 
            zip(zero_indices, period_lengths)]
            
        even_bins_y = bins_y[::2]
        odd_bins_y = bins_y[1::2]
        even_bins_x = bins_x[::2]
        odd_bins_x = bins_x[1::2]
        hi_peaks_x = []
        lo_peaks_x = []
        
        #check if even bin contains maxima
        if abs(even_bins_y[0].max()) > abs(even_bins_y[0].min()):
            hi_peaks = [bin.max() for bin in even_bins_y]
            lo_peaks = [bin.min() for bin in odd_bins_y]
            # get x values for peak
            for bin_x, bin_y, peak in zip(even_bins_x, even_bins_y, hi_peaks):
                hi_peaks_x.append(bin_x[np.where(bin_y==peak)[0][0]])
            for bin_x, bin_y, peak in zip(odd_bins_x, odd_bins_y, lo_peaks):
                lo_peaks_x.append(bin_x[np.where(bin_y==peak)[0][0]])
        else:
            hi_peaks = [bin.max() for bin in odd_bins_y]
            lo_peaks = [bin.min() for bin in even_bins_y]
            # get x values for peak
            for bin_x, bin_y, peak in zip(odd_bins_x, odd_bins_y, hi_peaks):
                hi_peaks_x.append(bin_x[np.where(bin_y==peak)[0][0]])
            for bin_x, bin_y, peak in zip(even_bins_x, even_bins_y, lo_peaks):
                lo_peaks_x.append(bin_x[np.where(bin_y==peak)[0][0]])
        
        max_peaks = [[x, y] for x,y in zip(hi_peaks_x, hi_peaks)]
        min_peaks = [[x, y] for x,y in zip(lo_peaks_x, lo_peaks)]
        
        return [max_peaks, min_peaks]
            
        
    def _smooth(x, window_len=11, window='hanning'):
        """
        smooth the data using a window of the requested size.
        
        This method is based on the convolution of a scaled window on the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        
        input:
            x: the input signal 
            window_len: the dimension of the smoothing window; should be an odd 
                integer
            window: the type of window from 'flat', 'hanning', 'hamming', 
                'bartlett', 'blackman'
                flat window will produce a moving average smoothing.
     
        output:
            the smoothed signal
            
        example:
     
        t = linspace(-2,2,0.1)
        x = sin(t)+randn(len(t))*0.1
        y = _smooth(x)
        
        see also: 
        
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, 
        numpy.convolve, scipy.signal.lfilter
     
        TODO: the window parameter could be the window itself if a list instead of
        a string   
        """
        if x.ndim != 1:
            raise ValueError, "smooth only accepts 1 dimension arrays."
     
        if x.size < window_len:
            raise ValueError, "Input vector needs to be bigger than window size."
        
        if window_len<3:
            return x
        
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise(ValueError,
                "Window is not one of '{0}', '{1}', '{2}', '{3}', '{4}'".format(
                *('flat', 'hanning', 'hamming', 'bartlett', 'blackman')))
        
        s = np.r_[x[window_len-1:0:-1], x, x[-1:-window_len:-1]]
        #print(len(s))
        if window == 'flat': #moving average
            w = np.ones(window_len,'d')
        else:
            w = eval('np.' + window + '(window_len)')
     
        y = np.convolve(w / w.sum(), s, mode = 'valid')
        return y
        
        
    def zero_crossings(y_axis, window = 11):
        """
        Algorithm to find zero crossings. Smoothens the curve and finds the
        zero-crossings by looking for a sign change.
        
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find zero-crossings
        window -- the dimension of the smoothing window; should be an odd integer
            (default: 11)
        
        return -- the index for each zero-crossing
        """
        # smooth the curve
        length = len(y_axis)
        x_axis = np.asarray(range(length), int)
        
        # discard tail of smoothed signal
        y_axis = _smooth(y_axis, window)[:length]
        zero_crossings = np.where(np.diff(np.sign(y_axis)))[0]
        indices = [x_axis[index] for index in zero_crossings]
        
        # check if zero-crossings are valid
        diff = np.diff(indices)
        if diff.std() / diff.mean() > 0.2:
            print diff.std() / diff.mean()
            print np.diff(indices)
            raise(ValueError, 
                "False zero-crossings found, indicates problem {0} or {1}".format(
                "with smoothing window", "problem with offset"))
        # check if any zero crossings were found
        if len(zero_crossings) < 1:
            raise(ValueError, "No zero crossings found")
        
        return indices 
        # used this to test the fft function's sensitivity to spectral leakage
        #return indices + np.asarray(30 * np.random.randn(len(indices)), int)
        # Calculate X profile for page split
    def find_X_Profile(xPointsUp,min_x,min_y):
        if ((xPointsUp-0.1)<=min_x) and (xPointsUp+0.1)<max_x:
            if xPointsUp<min_x:
                xPointBelow= np.arange(min_x,(xPointsUp+0.1+(min_x-xPointsUp)),0.01)
                xPointBelow = xPointBelow[abs(xPointBelow-xPointsUp)>0.001]
            else:
                xPointBelow= np.arange(min_x,(xPointsUp+0.1),0.01)
                xPointBelow = xPointBelow[abs(xPointBelow-xPointsUp)>0.001]
        
        if ((xPointsUp-0.1)>min_x) and (xPointsUp+0.1)>=max_x:
            if xPointsUp>max_x:
                xPointBelow=np.arange((xPointsUp-0.1-(xPointsUp-max_x)),max_x,0.01)
                xPointBelow = xPointBelow[abs(xPointBelow-xPointsUp)>0.001]
            else:
                xPointBelow=np.arange((xPointsUp-0.1),max_x,0.01)
                xPointBelow = xPointBelow[abs(xPointBelow-xPointsUp)>0.001]
        
        if ((xPointsUp-0.1)>min_x) and (xPointsUp+0.1)<max_x:
            xPointBelow=np.arange((xPointsUp-0.1),(xPointsUp+0.1),0.01)
            xPointBelow = xPointBelow[abs(xPointBelow-xPointsUp)>0.001]
        
        if ((xPointsUp-0.1)<min_x) and (xPointsUp+0.1)>max_x:
            xPointBelow=np.arange((xPointsUp-0.1),(xPointsUp+0.1),0.01)
            xPointBelow = xPointBelow[abs(xPointBelow-xPointsUp)>0.001]
        
        slopeTemp = np.divide(1,np.subtract(xPointsUp,xPointBelow))
        
        func1 = np.vectorize(findIntercept)

        intercept = func1(xPointBelow,xPointsUp)
        
        countArray = np.ndarray((np.size(slopeTemp),1),int)

        
        for i in range(0,np.size(slopeTemp)):
            ixA = calculateIntersectionA(slopeTemp[i],intercept[i])
            ixB = calculateIntersectionB(slopeTemp[i],intercept[i])
            tempB = np.multiply(ixA,ixB);
            ixC = calculateIntersectionC(slopeTemp[i],intercept[i])
            ixD = calculateIntersectionD(slopeTemp[i],intercept[i])
            tempC = np.multiply(ixC,ixD)
            tempB = tempB<0;
            tempC = tempC<0;
            countArray[i] = np.size(np.ix_(tempB | tempC))
    
            
        return np.min(countArray)
          
    
    def findIntercept(coor2,coor1):
        slope = np.divide(1,np.subtract(coor1,coor2))
        b = np.subtract(1,np.multiply(slope,coor1))
        return b
    
    def calculateIntersectionA(s,i):
        # s = slope and i = intercept
        return np.add(np.multiply(s,preFilteredData[indexToConsider,1]),np.subtract(i,preFilteredData[indexToConsider,2]))
    
    def calculateIntersectionB(s,i):
        return np.add(np.multiply(s,preFilteredData[indexToConsider,3]),np.subtract(i,preFilteredData[indexToConsider,4]))
    
    def calculateIntersectionC(s,i):
        return np.add(np.multiply(s,preFilteredData[indexToConsider,1]),np.subtract(i,preFilteredData[indexToConsider,4]))
    
    def calculateIntersectionD(s,i):
        return np.add(np.multiply(s,preFilteredData[indexToConsider,3]),np.subtract(i,preFilteredData[indexToConsider,2]))    
    
    # Supporter functions
    def movingaverage(interval, window_size):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')
    
    def calculateCutPointIx(actualPeaks,range_):
        cut_ = -1;    
        for pk in actualPeaks:
            if np.any(pk[0]==range_):
                cut_ =  pk[0]
                break;
        return cut_
    
    def distCalulationNew(a,b):
        distWord = np.subtract(a[:,[1,2]],b);
        distWord = np.power(distWord,2);
        distWord1 = np.power(np.sum(distWord,axis=1),0.5);
        
        distWord = np.subtract(a[:,[3,2]],b);
        distWord = np.power(distWord,2);
        distWord2 = np.power(np.sum(distWord,axis=1),0.5);
        
        distWord = np.subtract(a[:,[1,4]],b);
        distWord = np.power(distWord,2);
        distWord3 = np.power(np.sum(distWord,axis=1),0.5);
        
        distWord = np.subtract(a[:,[3,4]],b);
        distWord = np.power(distWord,2);
        distWord4 = np.power(np.sum(distWord,axis=1),0.5);
        
        distVec = np.array([distWord1,distWord2,distWord3,distWord4])
        
        return distVec
    
    # Neural Netwrok Parameters
    # Netwrok Weight Matrix            
    IW =np.matrix( np.array([[-5.4418  , 37.4529  ,  5.5736  , -4.5354  ,  0.4307 ,   0.0395  , 0.1616],
                   [-0.6640 ,  15.6633  ,  0.4456 ,   0.3437,  -11.2914 ,  -0.2126 ,   1.0719],
                    [-1.8122 , -26.8527 ,  12.5663  ,  0.0969 ,  -0.0094  , -0.0634  , -0.0037],
                    [-0.4184 ,   3.3215 ,  -0.1944  , -0.2692 ,  -0.0030 ,   0.0461  , -0.0519],
                    [0.3392  , -8.2592  , -6.1236 , -25.1874  , -0.2366 ,  -0.1298  ,  0.1672],
                    [1.2716  , 26.1854 ,  16.0628 ,  25.8461  ,  2.5596 , -78.0128  , 20.9898],
                    [0.1675 ,  26.0839 , 409.1064  ,  4.5132  , -0.3801  , -0.0157 ,   0.4406],
                    [-0.6780 , -27.2737  , -1.4170 , -36.0104  ,  0.1094  , -0.0361,   -0.0715]])  ) 
                    
    # Bias for hidden layer    
    b1 = np.matrix(np.array([[ 44.1387],
        [30.3000],
      [-13.3406],
        [4.4684],
       [-26.1089],
        [-27.0020],
      [438.3794],
      [-43.9163]])   )
    
    # Bias for output layer
    b2 = np.matrix(np.array([[15.6106],
                    [-14.9825]]))
    
    LW =np.matrix( np.array([[ 0.7723,  -37.6731 ,  -1.2153 , -33.4960  , -3.4024  ,  0.2162  , 48.6920  ,  2.5112],
                   [-1.9791,   36.9998  ,  1.6843 ,  32.7260  ,  5.1717  , -1.1162,  -49.3584 ,  -2.7970]])     )
    
    maxVec = np.array([0.9399 , 112.0000 ,   0.0399 , 147.0000   , 1.0000   , 0.9990   , 0.9844]);
    minVec = np.array([0     ,    0   ,      0 , -55.4060 ,  -1.0000    ,     0    ,     0]);
    
    # Neural netwrok activation function
    def tansig(dat):
        return np.subtract(np.divide(2,(1+np.exp(np.multiply(-2,dat)))),1);
    
    def softmax(dat):
        temp=np.exp(dat)
        tempSum = np.sum(temp)
        out = np.divide(temp,tempSum)
        return out
        
    # Neural Network Simulation funtion
    def nnSim(normDat,IW,LW,b1,b2):
        hiddenOutput = tansig(IW*normDat + b1);
        outputActivation = (LW*hiddenOutput + b2)
        return softmax(outputActivation)
    #Extract word coordinate information, ocr conf and height and width information
    fileName1 = "%s%s"%(filePath,fileName) #"53211844_160.xml"
    soup = bs4.BeautifulSoup(open(fileName1)) #51150019_1 - test 379_1 ; 2271337_13 - test id=6, 380_13; 45949734_1 , 45444878_5, 53211844_160 - 132 and 160; 48898051_301 131 and 301 ; 45509238_1 - 128 and 1; 45977751_1 128 and 
    pageInfo = soup.find_all('div',class_="ocr_page")# id='page_1'
    if pageInfo.__len__()>1:
        f_log = open("multiple-page-errors.txt","a")
        pageInfo = pageInfo[0];
        soup=pageInfo  
        f_log.write("\nMultiple page error : Image file path- %s hOCR file path- %s. Processing first page only."%(pageInfo["title"].split(';')[0],fileName1))
        f_log.close()
    t_x,t_y,pageWidth,pageHeight = pageInfo["title"].split(';')[1].split('bbox ')[1].split(' ')
    pageWidth = float(pageWidth)
    pageHeight = float(pageHeight)
    
    allSpanTags = [];
    allSpanTags=soup.find_all("span",class_="ocrx_word")
    
    wordInfo = np.ndarray((allSpanTags.__len__(),8))
    wordInfoNon_Scaled = np.ndarray((allSpanTags.__len__(),8))
    for val in allSpanTags:
        splitList = val["title"].split(';')
        x1,y1,x2,y2 = splitList[0].split('bbox ')[1].split(' ')
        w_conf = float(splitList[1].split('x_wconf ')[1])/100
        word_id = int(val["id"].split("word_")[1])
        wordInfoNon_Scaled[word_id-1,:]= np.array([word_id, int(x1),int(y1),int(x2),int(y2),abs(int(y2) - int(y1)), abs(int(x2) - int(x1)),w_conf])
        x1 = (int(x1)/pageWidth)
        y1 = (1 - (int(y1)/pageHeight))
        x2 = (int(x2)/pageWidth)
        y2 = (1 - (int(y2)/pageHeight))
        height = (abs(y2 - y1))
        width = (abs(x2 - x1))
        #print np.float16(np.array([word_id, x1,y1,x2,y2,height, width,w_conf])) 
        #print word_id-1,(np.array([word_id,]))
        wordInfo[word_id-1,:]= (np.array([word_id, x1,y1,x2,y2,height, width,w_conf])) 
        
    #PreDenoise
    preDeNoiseParameters = [0,0.9100,2.0000,0.9900];
    # 1. Confidence Filter
    ixFilter = wordInfo[:,7]<preDeNoiseParameters[1];
    ixFilter1 = wordInfo[:,7]>preDeNoiseParameters[0]
    ixFilter = ixFilter & ixFilter1
    
    # 2. Height and Width Filter
    ixHeightWidthFilter = np.divide(wordInfo[:,5],wordInfo[:,6])< preDeNoiseParameters[2];
    
    tempFilter = ixFilter & ixHeightWidthFilter
    
    if np.size(tempFilter)>1:
        # 3. Area Filter
        area_bboxes = np.multiply(wordInfo[:,5],wordInfo[:,6])
        area_descend = np.sort(area_bboxes[tempFilter])[::-1]
        area_descend_cumsum=(np.cumsum(area_descend)/np.sum(area_descend))
        areaThInd = area_descend_cumsum>=preDeNoiseParameters[3]
        if np.any(areaThInd):
            areaTh=area_descend[areaThInd][0]
            ixAreaFilter = area_bboxes>areaTh
            finalFilter = tempFilter & ixAreaFilter
        else:
            finalFilter = tempFilter
        preFilteredData = wordInfo[finalFilter,:]
        
        if np.any(finalFilter):
            # Calculate page bounds after preDenoising
            max_x =(np.max(wordInfo[finalFilter,3]));
            max_y = (np.max(wordInfo[finalFilter,2]));
            min_x = (np.min(wordInfo[finalFilter,1]));
            min_y = (np.min(wordInfo[finalFilter,4]));
            
            #Number of bounding boxes after preDenoising
            numBbox = np.size(np.ix_(finalFilter))
            
            # Page Splitting algorithm
            # 1. x_Intersection profile
            xPointsUp = (np.arange(min_x,max_x,((max_x-min_x)/1000)))#min_x:(max_x-min_x)/1000:max_x;
            stepFromTop=(0.2*(max_y-min_y)) # range to consider. Removing top and bottom 20% bboxes
            indexToConsider = preFilteredData[:,2]<((max_y-stepFromTop))
            indexToConsiderTemp = preFilteredData[:,4]>((min_y+stepFromTop))
            indexToConsider = indexToConsider & indexToConsiderTemp;    
            xProfileFunc = np.vectorize(find_X_Profile)
            intersectionCountProfile = xProfileFunc(xPointsUp,min_x,min_y)
            
            # Smooth the signal
            zerosIndex = np.ix_(intersectionCountProfile==0);
            for intIndex in range(1,(np.size(zerosIndex)-1)):
                if(intersectionCountProfile[zerosIndex[0][intIndex]+1]!=0 and intersectionCountProfile[zerosIndex[0][intIndex]-1]!=0):
                    intersectionCountProfile[zerosIndex[0][intIndex]] = intersectionCountProfile[zerosIndex[0][intIndex]-1];
            
            # Smoothing intersection profile by taking 20 point moving average.
            intersectionCountProfile=movingaverage(intersectionCountProfile,20)
        #    pl.figure()        
        #    pl.plot(intersectionCountProfile)
            # 75th percentile of intersection profile for normalizing 
            prcOutputMovAvg = (np.percentile(intersectionCountProfile,80))
            if prcOutputMovAvg>0.0:
                negIntersectionCountProfile = -(intersectionCountProfile/prcOutputMovAvg);
            else:
                negIntersectionCountProfile = -(intersectionCountProfile)
            
            # Find CutPoints
            #NOTE : For future work below code can be generalized to handle any number of columns. Right now it can handle upto 4 columns on a page image
        
            max_,min_ = peakdetect(negIntersectionCountProfile,lookahead=150,delta=np.diff(negIntersectionCountProfile).max() * 2)
            print max_, type(max_)       
            peakThreshold = -0.1
            acceptedPeaks = [];
            for pk in max_:
                if pk[1]>peakThreshold:
                    if np.any(pk[0]==np.arange(199,799)):
                        acceptedPeaks.append(pk)
            
            cutPoints=np.array([-1.0,-1.0,-1.0]);
            if np.any(negIntersectionCountProfile[199:398]==0):
                temp = np.arange(199,398)
                tempCutPoints=xPointsUp[temp[negIntersectionCountProfile[199:398]==0]]
                cutPoints[0]=(np.mean(100*tempCutPoints))/100.0
            else:
                ix_ = calculateCutPointIx(acceptedPeaks,np.arange(199,399))
                if ix_!=-1:
                    cutPoints[0] = xPointsUp[ix_]
                
                
            if np.any(negIntersectionCountProfile[400:599]==0):
                temp = np.arange(400,599)
                tempCutPoints=xPointsUp[temp[negIntersectionCountProfile[400:599]==0]];
                cutPoints[1] =(np.mean(100*tempCutPoints))/100.0
            else:
                ix_ = calculateCutPointIx(acceptedPeaks,np.arange(400,599))
                if ix_!=-1:
                    cutPoints[1] = xPointsUp[ix_]
        
            if np.any(negIntersectionCountProfile[600:799]==0):
                temp = np.arange(600,799)
                tempCutPoints=xPointsUp[temp[negIntersectionCountProfile[600:799]==0]];
                cutPoints[2] = (np.mean(100*tempCutPoints))/100.0
            else:
                ix_ = calculateCutPointIx(acceptedPeaks,np.arange(600,799))
                if ix_!=-1:
                    cutPoints[2] = xPointsUp[ix_]
            if (np.size(np.ix_(negIntersectionCountProfile==0))/float(np.size(negIntersectionCountProfile)))>=0.5:
                temp = np.arange(399,599)
                cutPoints[2] =(np.mean(100*tempCutPoints))/100.0
            # Filter each coloumn
            numCutPoints = np.size(np.ix_(cutPoints!=-1));
            if numCutPoints==0:
                numCutPoints=1
                cutPointsLocs = cutPoints[cutPoints!=-1]
            else: 
                cutPointsLocs = cutPoints[cutPoints!=-1];
                numCutPoints = numCutPoints +1;
            
            predictedLabelMachineLearning = np.array([])
            confVal = np.ones(finalFilter.shape);
            for cutPointIdx in range(0,numCutPoints):
                tempCutPoint = 0.0;
                if np.size(cutPointsLocs)==0:
                    indexToConsider = preFilteredData[:,1]<=max_x;
                    actualIndexToConsider = wordInfo[:,1]<=1;
                    tempCutPoint=np.copy(max_x);
                else:
                    cutPointLocsSize = np.size(cutPointsLocs)
                    if cutPointLocsSize==1 and cutPointIdx==0:
                        indexToConsider = preFilteredData[:,3]<=cutPointsLocs[cutPointIdx]
                        tempCutPoint=cutPointsLocs[cutPointIdx];
                        actualIndexToConsiderTemp = wordInfo[:,3]<=cutPointsLocs[cutPointIdx] 
                        actualIndexToConsiderTemp1 =cutPointsLocs[cutPointIdx]>wordInfo[:,1] 
                        actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);
                        actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                    
                    
                    if cutPointLocsSize==1 and cutPointIdx==1:
                        indexToConsider = preFilteredData[:,1]>cutPointsLocs[cutPointIdx-1]
                        actualIndexToConsider = wordInfo[:,1]>cutPointsLocs[cutPointIdx-1];
                        tempCutPoint=cutPointsLocs[cutPointIdx-1];
                    
                    if cutPointLocsSize==2 and cutPointIdx==0:
                        indexToConsider = preFilteredData[:,3]<=cutPointsLocs[cutPointIdx]
                        actualIndexToConsiderTemp = wordInfo[:,3]<=cutPointsLocs[cutPointIdx] 
                        actualIndexToConsiderTemp1 = cutPointsLocs[cutPointIdx]>wordInfo[:,1] 
                        actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);
                        actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                        tempCutPoint=cutPointsLocs[cutPointIdx];
                        
                    if cutPointLocsSize==2 and cutPointIdx==1:
                        indexToConsider = preFilteredData[:,1]>cutPointsLocs[cutPointIdx-1]
                        indexToConsider = indexToConsider & (preFilteredData[:,3]<=cutPointsLocs[cutPointIdx])
                        preActualIndexToConsider = np.copy(actualIndexToConsider);
                        actualIndexToConsiderTemp = (wordInfo[:,1]>cutPointsLocs[cutPointIdx-1]) 
                        actualIndexToConsiderTemp = actualIndexToConsiderTemp & (wordInfo[:,3]<=cutPointsLocs[cutPointIdx]) 
                        actualIndexToConsiderTemp1 = cutPointsLocs[cutPointIdx]>wordInfo[:,1]
                        actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);# or 
                        actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                        actualIndexToConsider[actualIndexToConsider & preActualIndexToConsider]=0;
                        tempCutPoint=cutPointsLocs[cutPointIdx-1];
                    
                    if cutPointLocsSize==2 and cutPointIdx==2:
                        indexToConsider = preFilteredData[:,1]>cutPointsLocs[cutPointIdx-1]
                        actualIndexToConsider = wordInfo[:,1]>cutPointsLocs[cutPointIdx-1];
                        tempCutPoint=cutPointsLocs[cutPointIdx-1];
                        
                    if cutPointLocsSize==3 and cutPointIdx==0:
                        indexToConsider = preFilteredData[:,3]<=cutPointsLocs[cutPointIdx]
                        actualIndexToConsiderTemp = wordInfo[:,3]<=cutPointsLocs[cutPointIdx] 
                        actualIndexToConsiderTemp1 = cutPointsLocs[cutPointIdx]>wordInfo[:,1] 
                        actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);
                        actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                        actualIndexToConsider_1 = np.copy(actualIndexToConsider);
                        tempCutPoint=cutPointsLocs[cutPointIdx];
                    
                    if cutPointLocsSize==3 and (cutPointIdx==1 or cutPointIdx==2):
                        indexToConsider = preFilteredData[:,1]>cutPointsLocs[cutPointIdx-1]
                        indexToConsider = indexToConsider & (preFilteredData[:,3]<=cutPointsLocs[cutPointIdx])
                        preActualIndexToConsider = np.copy(actualIndexToConsider);
                        actualIndexToConsiderTemp = (wordInfo[:,1]>cutPointsLocs[cutPointIdx-1]) 
                        actualIndexToConsiderTemp = actualIndexToConsiderTemp & (wordInfo[:,3]<=cutPointsLocs[cutPointIdx]) 
                        actualIndexToConsiderTemp1 = cutPointsLocs[cutPointIdx]>wordInfo[:,1] 
                        actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);
                        actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                        actualIndexToConsider[actualIndexToConsider & preActualIndexToConsider]=0;
                        if(cutPointIdx==3):
                            actualIndexToConsider[actualIndexToConsider & actualIndexToConsider_1]=0;
                        tempCutPoint=cutPointsLocs[cutPointIdx-1];
                        
                    if cutPointLocsSize==3 and cutPointIdx==3:
                        indexToConsider = (preFilteredData[:,1]>cutPointsLocs[cutPointIdx-1])
                        actualIndexToConsider = wordInfo[:,1]>cutPointsLocs[cutPointIdx-1];
                        tempCutPoint=cutPointsLocs[cutPointIdx-1];
                    
                    # Iterative - NN filter
                bboxcenterRelabellingActual = wordInfo[actualIndexToConsider,:];
                k=11;
                alpha = 7;
                max_iter = 20;
                k1=k;k2=k;k3=k;k4=k;
                finalFilterTemp = finalFilter[actualIndexToConsider];
                finalFilterTemp1 = np.zeros(finalFilterTemp.shape)
                finalFilterTemp1[finalFilterTemp]=1;
                finalFilterTemp = finalFilterTemp1;
                finalFilterTemp[finalFilterTemp==0] = -1;
                tempHeight = bboxcenterRelabellingActual[:,5];
                tempWidth = bboxcenterRelabellingActual[:,6];
                prevfinalFilterTemp = 999;
                
                if np.size(preFilteredData[indexToConsider,5])>0:
                    iqrHeight = np.percentile(preFilteredData[indexToConsider,5],[25,75])
                    iqrHeight = abs(iqrHeight[0] - iqrHeight[1])
                    medianHeight = np.median(preFilteredData[indexToConsider,5])
                    D_max = medianHeight + alpha*iqrHeight
                    if np.size(finalFilterTemp)==1:
                        iqrHeight=1.0;
                else:
                    D_max = 0;
                    medianHeight = 0;
                    iqrHeight = 1.0
                
                confTemp = wordInfo[actualIndexToConsider,7];
                iter_ = 0;
                count_ = 0;
                numPrevError = -999;
                numCurrentError = 0;
                onlyOneBoxFlag = 0;
                if np.size(finalFilterTemp)==1:
                    onlyOneBoxFlag=1;
                while(((np.size(np.ix_(finalFilterTemp!=prevfinalFilterTemp)) > 1) and (iter_< max_iter) and (count_<3)) or onlyOneBoxFlag==1): 
                    numCurrentError = (np.size(np.ix_(finalFilterTemp!=prevfinalFilterTemp)))
                    if numPrevError==numCurrentError:
                        count_ = count_+1;
                    numPrevError=numCurrentError    
                    #print iter_  ,(np.size(np.ix_(finalFilterTemp!=prevfinalFilterTemp)))              
                    iter_ = iter_ + 1;
                    prevfinalFilterTemp = np.copy(finalFilterTemp);
                    preLabel = np.copy(finalFilterTemp);
                    for word in range(0,np.size(finalFilterTemp)):
                        k1=k;k2=k;k3=k;k4=k;
                        fillterWord = np.ones(finalFilterTemp.shape);
                        fillterWord[word] = 0;
                        kNeigh=np.array([]);
                        remainingBbox = fillterWord==1
                        wordInOrgDoc = bboxcenterRelabellingActual[word,:];                    
                        dist1 = np.min(distCalulationNew(bboxcenterRelabellingActual[remainingBbox,:],wordInOrgDoc[[1,2]]),axis=0)
                        dist2 = np.min(distCalulationNew(bboxcenterRelabellingActual[remainingBbox,:],wordInOrgDoc[[1,4]]),axis=0)
                        dist3 = np.min(distCalulationNew(bboxcenterRelabellingActual[remainingBbox,:],wordInOrgDoc[[3,2]]),axis=0)
                        dist4 = np.min(distCalulationNew(bboxcenterRelabellingActual[remainingBbox,:],wordInOrgDoc[[3,4]]),axis=0)
                        
                        selInd1 = np.ix_(dist1<D_max);
                        selInd2 = np.ix_(dist2<D_max);
                        selInd3 = np.ix_(dist3<D_max);
                        selInd4 = np.ix_(dist4<D_max);
                        
                        if np.size(selInd1)<k:
                            k1 = np.size(selInd1)
                        
                        if np.size(selInd2)<k:
                            k2 = np.size(selInd2)    
                        
                        if np.size(selInd3)<k:
                            k3 = np.size(selInd3)
                        
                        if np.size(selInd4)<k:
                            k4 = np.size(selInd4)
                            
                        if np.any(np.array([k1,k2,k3,k4])>0):
                            ind1 = np.argsort(dist1[selInd1])
                            val1 = dist1[selInd1[0][ind1]]
                            
                            ind2 = np.argsort(dist2[selInd2])
                            val2 = dist2[selInd2[0][ind2]]
        
                            ind3 = np.argsort(dist3[selInd3])
                            val3 = dist3[selInd3[0][ind3]]                                           
                            
                            ind4 = np.argsort(dist4[selInd4])
                            val4 = dist4[selInd4[0][ind4]]
                            remainingBbox = np.ix_(remainingBbox)
                            if k1!=0:
                                index = ind1;
                                kNeigh = np.array([dist1[selInd1[0][index[range(0,k1)]]],finalFilterTemp[remainingBbox[0][selInd1[0][index[range(0,k1)]]]]]);
        
                            if k2!=0:
                                index = ind2;
                                if np.size(kNeigh)>0:
                                    kNeigh = np.append(kNeigh,np.array([dist2[selInd2[0][index[range(0,k2)]]],finalFilterTemp[remainingBbox[0][selInd2[0][index[range(0,k2)]]]]]),1);                            
                                else:
                                    kNeigh = np.array([dist2[selInd2[0][index[range(0,k2)]]],finalFilterTemp[remainingBbox[0][selInd2[0][index[range(0,k2)]]]]])
                                
                                
                            if k3!=0:
                                index = ind3[range(0,k3)];
                                
                                for i3 in range(0,np.size(index)):
                                    if k1!=0:
                                        if np.any(index[i3]==ind1[range(0,k1)]):
                                            index[i3] = -999
                                    else:
                                        break
                                index = index[index!=-999]
                                k3 = np.size(index)
                                if k3!=0:
                                    if np.size(kNeigh)>0:
                                        kNeigh = np.append(kNeigh,np.array([dist3[selInd3[0][index[range(0,k3)]]],finalFilterTemp[remainingBbox[0][selInd3[0][index[range(0,k3)]]]]]),1);    
                                    else:
                                        kNeigh = np.array([dist3[selInd3[0][index[range(0,k3)]]],finalFilterTemp[remainingBbox[0][selInd3[0][index[range(0,k3)]]]]])
                                        
                                
                            if k4!=0:
                                index = ind4[range(0,k4)];
                                for i4 in range(0,np.size(index)):
                                    if k2!=0:
                                        if np.any(index[i4]==ind2[range(0,k2)]):
                                            index[i4] = -999
                                    else:
                                        break
                                index = index[index!=-999]
                                k4 = np.size(index)
                                if k4!=0:
                                    if np.size(kNeigh)>0:
                                        kNeigh = np.append(kNeigh,np.array([dist4[selInd4[0][index[range(0,k4)]]],finalFilterTemp[remainingBbox[0][selInd4[0][index[range(0,k4)]]]]]),1);    
                                    else:
                                        kNeigh = np.array([dist4[selInd4[0][index[range(0,k4)]]],finalFilterTemp[remainingBbox[0][selInd4[0][index[range(0,k4)]]]]])
                                
                            if np.size(kNeigh)>0:
                                wNeigh = np.divide(1,kNeigh[0,:])
                                for inD in range(0,np.size(wNeigh)):
                                    if np.isnan(wNeigh[inD]) or np.isinf(wNeigh[inD]):
                                        wNeigh[inD]=1.0;
                                preLabel[word] = np.divide(np.sum(np.multiply(kNeigh[1,:],wNeigh)),np.sum(wNeigh))
        
                    xTemp = np.array([])
                    bbox_center = np.array([np.mean(bboxcenterRelabellingActual[:,[1,3]],axis=1),np.mean(bboxcenterRelabellingActual[:,[2,4]],axis=1)]);
                    y_dist1 = abs(1-bbox_center[1,:]);
                    x_dist1 = abs(tempCutPoint-bbox_center[0,:]);
                    
                    xTemp = np.array([confTemp,np.divide(tempHeight,tempWidth),np.multiply(tempHeight,tempWidth),np.divide(np.subtract(tempHeight,medianHeight),iqrHeight),preLabel,y_dist1,x_dist1])
                    removeBboxesWithConf = xTemp[0,:]<0.95;
                    removeRatioInf = np.isinf(xTemp[1,:])
                    removeRatioInf1 = ~removeRatioInf
                    removeRatioNan = np.isnan(xTemp[1,:])
                    removeRatioNan1 = ~removeRatioNan
                    fullRemove = removeBboxesWithConf & removeRatioInf1 & removeRatioNan1
                    xTemp= xTemp[:,fullRemove];
                    normX = np.zeros(xTemp.shape)
                    for v in range(0,xTemp.shape[0]):
                        normX[v,:] = np.divide(np.subtract(xTemp[v,:],minVec[v]),(maxVec[v] - minVec[v]))
                    for v in range(0,xTemp.shape[0]):
                        normX[v,:] = 2*normX[v,:] -1
                    normX = np.matrix(normX);
                    confValTemp = 0.95*np.ones(finalFilterTemp.shape);
                    confValTempAfterConfRem = confValTemp[removeBboxesWithConf] 
                    tempPred = finalFilterTemp[removeBboxesWithConf]
                    for col in range(0,normX.shape[1]):
                        simOut = nnSim(normX[:,col],IW,LW,b1,b2)   
                        index_max=np.argmax(simOut)
                        max_value = simOut[index_max]
                       # print max_value
                        confValTempAfterConfRem[col] = max_value
                        if index_max==1:
                            tempPred[col] = -1
                        else:
                            tempPred[col] = 1
                    confValTemp[removeBboxesWithConf] = confValTempAfterConfRem;
                    finalFilterTemp[removeBboxesWithConf]  = tempPred
                    if np.size(finalFilterTemp)==1:
                        onlyOneBoxFlag=0;
                    #New addition
                    #finalFilterTemp[removeRatioInf]=-1
                    #finalFilterTemp[removeRatioNan]=-1
                    
                    
                indactualIndexToConsider= np.ix_(actualIndexToConsider)[0];
                #print np.size(indactualIndexToConsider)
                confVal[indactualIndexToConsider[finalFilterTemp==1]] = confValTemp[finalFilterTemp==1]
                confVal[indactualIndexToConsider[finalFilterTemp==-1]] = confValTemp[finalFilterTemp==-1]
                if np.size(predictedLabelMachineLearning)>0:
                    predictedLabelMachineLearning = np.append(predictedLabelMachineLearning,indactualIndexToConsider[finalFilterTemp==1],1)     
                else:                
                    predictedLabelMachineLearning = indactualIndexToConsider[finalFilterTemp==1]
            
            MLFilter = np.zeros(finalFilter.shape)
            MLFilter[predictedLabelMachineLearning]  = 1;
            
             
            #make two hOCR files
            soup1 = bs4.BeautifulSoup(open(fileName1))
            for word_id in range(0,np.size(wordInfo[:,0])):
               # print word_id,
                temp = soup.find("span",class_="ocrx_word",id="word_%d"%(wordInfo[word_id,0]))
                temp['title'] = "%s; pred %d; predConf %.4f"%(temp['title'],MLFilter[word_id],confVal[word_id])
                if MLFilter[word_id]==0:
                    temp1 = soup1.find("span",class_="ocrx_word",id="word_%d"%(wordInfo[word_id,0]))
                    temp1.extract()
            
            f = open("%s%s_SEASR.xml"%(filePath,fileName.replace('.xml','')),'w')
            f.write(soup.encode())
            f.close()
            
#            toDel = np.ix_(MLFilter==0)[0]
#            soup1 = bs4.BeautifulSoup(open(fileName1))
#            for word_id in range(0,np.size(toDel)):
#                temp = soup1.find("span",class_="ocrx_word",id="word_%d"%(wordInfo[toDel[word_id],0]))
#                temp.extract()
            
            f = open("%s%s_IDHMC.xml"%(filePath,fileName.replace('.xml','')),'w')
            f.write(soup1.encode())
            f.close()
        else:
            #make two hOCR files
            for word_id in range(0,np.size(wordInfo[:,0])):
                temp = soup.find("span",class_="ocrx_word",id="word_%d"%(wordInfo[word_id,0]))
                temp['title'] = "%s; pred %d; predConf %.4f"%(temp['title'],-1,-1)
        
            f = open("%s%s_SEASR.xml"%(filePath,fileName.replace('.xml','')),'w')
            f.write(soup.encode())
            f.close()
            soup1 = bs4.BeautifulSoup(open(fileName1))
            f = open("%s%s_IDHMC.xml"%(filePath,fileName.replace('.xml','')),'w')
            f.write(soup1.encode())
            f.close()       
    else:      
        #make two hOCR files
        for word_id in range(0,np.size(wordInfo[:,0])):
            temp = soup.find("span",class_="ocrx_word",id="word_%d"%(wordInfo[word_id,0]))
            temp['title'] = "%s; pred %d; predConf %.4f"%(temp['title'],-1,-1)
        
        f = open("%s%s_SEASR.xml"%(filePath,fileName.replace('.xml','')),'w')
        f.write(soup.encode())
        f.close()
        soup1 = bs4.BeautifulSoup(open(fileName1))
        f = open("%s%s_IDHMC.xml"%(filePath,fileName.replace('.xml','')),'w')
        f.write(soup1.encode())
        f.close()
        #print "Do Nothing and generate two hOCR with all bounding boxes as noise"
        # copy code for generating hOCR

def logError(fileObj,errorStr):
    fileObj.write(errorStr)
if __name__ == "__main__":
    parser = parser_opt.OptionParser()
    parser.add_option('-p', '--path',action="store", dest="filePath",help="hOCR file path", default="")
    parser.add_option('-n', '--name',action="store", dest="fileName",help="hOCR file name", default="")
    parser.add_option('-d', '--debug',action="store", dest="debugFlag",help="For debugging purpose", default="0")
    options, args = parser.parse_args()
   # f = open("%s_logFile_PSI_PostProcessing.txt"%(options.fileName.replace('.xml','')),'a')
   # ts = time.time()
   # st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S');  
#    try:
    #logError(f,"\n%s : Processing '%s'..."%(st,options.fileName))
    deNoise(options.filePath,options.fileName,options.debugFlag)
   # deNoise("C:/Users/guptaa.JAEN/Google Drive/EMOP/PythonImplDenoise/DeNoise/",'350_error.xml','0')#350
   # ts = time.time()
   # st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'); 
    #logError(f,"\n%s : Processing Completed."%(st))
        
        
            


    
    


