#!/usr/bin/env python

import os
import sys
import json
import numpy as np;
import parseOCR as p;
import peaks_find as pks;
#import matplotlib.pyplot as pl

def multiColumnDetect(inFile):
    infile=inFile
    # extract word bounding box information
    props=p.parseHOCR(infile)
    wordInfo = props[1]
    pageHeight = props[3]
    pageWidth = props[2]
    
    if wordInfo.size==0:
        return "",""
    def intersectArea(coor1,coor2):
        x11 = coor1[0]
        y11 = coor1[1]
        x12 = coor1[0] + coor1[2] # coor1[2] = width and coor1[3] = height
        y12 = coor1[1] + coor1[3]
        x21 = coor2[0]
        y21 = coor2[1]
        x22 = coor2[0] + coor2[2] # coor1[2] = width and coor1[3] = height
        y22 = coor2[1] + coor2[3]
        x_overlap = max(0,min(x12,x22)) - max(x11,x21)
        y_overlap = max(0,min(y12,y22)) - max(y11,y21)
        if x_overlap*y_overlap < 0.0 :
            return 0.0
        else:
            return x_overlap*y_overlap
    def findIntercept(coor2,coor1):
        slope = np.divide(1,np.subtract(coor1,coor2))
        b = np.subtract(1,np.multiply(slope,coor1))
        return b
    
    def calculateIntersectionA(s,i):
        # s = slope and i = intercept
        return np.add(np.multiply(s,wordInfo[indexToConsider,1]),np.subtract(i,wordInfo[indexToConsider,2]))
    
    def calculateIntersectionB(s,i):
        return np.add(np.multiply(s,wordInfo[indexToConsider,3]),np.subtract(i,wordInfo[indexToConsider,4]))
    
    def calculateIntersectionC(s,i):
        return np.add(np.multiply(s,wordInfo[indexToConsider,1]),np.subtract(i,wordInfo[indexToConsider,4]))
    
    def calculateIntersectionD(s,i):
        return np.add(np.multiply(s,wordInfo[indexToConsider,3]),np.subtract(i,wordInfo[indexToConsider,2]))
    
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
    
    def convertArrToTuple(arr):
        return arr[0]
    
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
    
    
    # Calculate page bounds
    max_x =(np.max(wordInfo[:,3]));
    max_y = (np.max(wordInfo[:,2]));
    min_x = (np.min(wordInfo[:,1]));
    min_y = (np.min(wordInfo[:,4]));
    
    
    # Page Splitting algorithm
    # 1. x_Intersection profile
    xPointsUp = (np.arange(min_x,max_x,((max_x-min_x)/1000)))#min_x:(max_x-min_x)/1000:max_x;
    stepFromTop=(0.2*(max_y-min_y)) # range to consider. Removing top and bottom 20% bboxes
    indexToConsider = wordInfo[:,2]<((max_y-stepFromTop))
    indexToConsiderTemp = wordInfo[:,4]>((min_y+stepFromTop))
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
    #NOTE : For future work code written below can be generalized to handle any number of columns. Right now it can handle upto 4 columns on a page image
    
    max_,min_ = pks.peakdetect(negIntersectionCountProfile,lookahead=150,delta=np.diff(negIntersectionCountProfile).max() * 2)
    # print max_, type(max_)       
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
    
    multiColPoints="%0.2f,%0.2f,%0.2f"
    cutPoints=cutPoints*pageWidth
    multiColPoints=multiColPoints%(cutPoints[0],cutPoints[1],cutPoints[2])
    
    """
    Skewness Measure
    """
    
    numWords=np.shape(wordInfo)[0]
    estimatedSkewAngle = np.zeros((numCutPoints,1))
    skewAngleStr=""
    for cutPointIdx in range(0,numCutPoints):
        tempCutPoint = 0.0;
        skewAngleStr = skewAngleStr + "%f,";
        prevCutPoint = np.copy(tempCutPoint);
        if np.size(cutPointsLocs)==0:
            actualIndexToConsider = wordInfo[:,1]<=1;
        else:
            cutPointLocsSize = np.size(cutPointsLocs)
            if cutPointLocsSize==1 and cutPointIdx==0:
                actualIndexToConsiderTemp = wordInfo[:,3]<=cutPointsLocs[cutPointIdx] 
                actualIndexToConsiderTemp1 =cutPointsLocs[cutPointIdx]>wordInfo[:,1] 
                actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);
                actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
            
            
            if cutPointLocsSize==1 and cutPointIdx==1:
                actualIndexToConsider = wordInfo[:,1]>cutPointsLocs[cutPointIdx-1];
            
            if cutPointLocsSize==2 and cutPointIdx==0:
                actualIndexToConsiderTemp = wordInfo[:,3]<=cutPointsLocs[cutPointIdx] 
                actualIndexToConsiderTemp1 = cutPointsLocs[cutPointIdx]>wordInfo[:,1] 
                actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);
                actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                tempCutPoint=cutPointsLocs[cutPointIdx];
                
            if cutPointLocsSize==2 and cutPointIdx==1:
                preActualIndexToConsider = np.copy(actualIndexToConsider);
                actualIndexToConsiderTemp = (wordInfo[:,1]>cutPointsLocs[cutPointIdx-1]) 
                actualIndexToConsiderTemp = actualIndexToConsiderTemp & (wordInfo[:,3]<=cutPointsLocs[cutPointIdx]) 
                actualIndexToConsiderTemp1 = cutPointsLocs[cutPointIdx]>wordInfo[:,1]
                actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);# or 
                actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                actualIndexToConsider[actualIndexToConsider & preActualIndexToConsider]=0;
                tempCutPoint=cutPointsLocs[cutPointIdx];
            
            if cutPointLocsSize==2 and cutPointIdx==2:
                actualIndexToConsider = wordInfo[:,1]>cutPointsLocs[cutPointIdx-1];
                
            if cutPointLocsSize==3 and cutPointIdx==0:
                actualIndexToConsiderTemp = wordInfo[:,3]<=cutPointsLocs[cutPointIdx] 
                actualIndexToConsiderTemp1 = cutPointsLocs[cutPointIdx]>wordInfo[:,1] 
                actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);
                actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                actualIndexToConsider_1 = np.copy(actualIndexToConsider);
                tempCutPoint=cutPointsLocs[cutPointIdx];
            
            if cutPointLocsSize==3 and (cutPointIdx==1 or cutPointIdx==2):
                preActualIndexToConsider = np.copy(actualIndexToConsider);
                actualIndexToConsiderTemp = (wordInfo[:,1]>cutPointsLocs[cutPointIdx-1]) 
                actualIndexToConsiderTemp = actualIndexToConsiderTemp & (wordInfo[:,3]<=cutPointsLocs[cutPointIdx]) 
                actualIndexToConsiderTemp1 = cutPointsLocs[cutPointIdx]>wordInfo[:,1] 
                actualIndexToConsiderTemp1 = actualIndexToConsiderTemp1 & (cutPointsLocs[cutPointIdx]<wordInfo[:,3]);
                actualIndexToConsider = actualIndexToConsiderTemp | actualIndexToConsiderTemp1
                actualIndexToConsider[actualIndexToConsider & preActualIndexToConsider]=0;
                if(cutPointIdx==3):
                    actualIndexToConsider[actualIndexToConsider & actualIndexToConsider_1]=0;
                tempCutPoint=cutPointsLocs[cutPointIdx];
                
            if cutPointLocsSize==3 and cutPointIdx==3:
                actualIndexToConsider = wordInfo[:,1]>cutPointsLocs[cutPointIdx-1];
            
            # Iterative - NN filter
        scaledWCoorFilteredwordCoordinates = wordInfo[actualIndexToConsider,:];
        numWords = np.shape(scaledWCoorFilteredwordCoordinates)[0]
        if np.size(scaledWCoorFilteredwordCoordinates)!=0:
            numLines = np.ceil(1.0/np.median(scaledWCoorFilteredwordCoordinates[:,5]))
            scaleNum = np.ceil(numWords/numLines)
            nBins = np.ceil(scaleNum*numLines)
            angleToVary = np.arange((4*np.pi)/9,(5*np.pi)/9,np.pi/900)
            entropyAngle = np.zeros(np.shape(angleToVary))
            for ang in range(0,np.size(angleToVary)):
               # print ang,
                InnerProduct = np.zeros((4*numWords,1))
                proj_vec = np.array([np.cos(angleToVary[ang]),np.sin(angleToVary[ang])])
                count=0.0;
                count_idx=0.0
                while count_idx<numWords:
                    InnerProduct[count]=np.sum(np.multiply(proj_vec,scaledWCoorFilteredwordCoordinates[count_idx,[1,2]]))
                    count=count+1;
                    InnerProduct[count]=np.sum(np.multiply(proj_vec,scaledWCoorFilteredwordCoordinates[count_idx,[3,2]]))
                    count=count+1;
                    InnerProduct[count]=np.sum(np.multiply(proj_vec,scaledWCoorFilteredwordCoordinates[count_idx,[1,4]]))
                    count=count+1;
                    InnerProduct[count]=np.sum(np.multiply(proj_vec,scaledWCoorFilteredwordCoordinates[count_idx,[3,4]]))
                    count=count+1;
                    count_idx=count_idx+1;
                hist,hist_edges=np.histogram(InnerProduct,bins=nBins,density=True)
                hist = hist*np.diff(hist_edges)
                entropyAngle[ang]=np.sum(np.multiply(-hist[hist!=0],np.log2(hist[hist!=0])))            
            angleDegree = (180*angleToVary)/np.pi;
            entropyAngle = movingaverage(entropyAngle,2)
            entropyAngle=np.delete(entropyAngle,0)
            angleDegree=np.delete(angleDegree,0)
            #pl.plot(angleDegree,entropyAngle)
            min_idx=np.argmin(entropyAngle)
            estimatedSkewAngle[cutPointIdx]=angleDegree[min_idx]-90.0;
        else:
            estimatedSkewAngle[cutPointIdx]=0.0;

    """
    Convert estinatedSkewAngle to string
    """
    skewAngleStr = skewAngleStr%tuple(map(convertArrToTuple,estimatedSkewAngle))
    
    return multiColPoints,skewAngleStr

if __name__=='__main__':
   input_file = sys.argv[1]
   multiColPoints,skewAngleStr = multiColumnDetect(input_file)
   data = {
       "multicol": multiColPoints,
       "skew_idx": skewAngleStr
   }
   print json.dumps(data)
   #print multiColPoints,skewAngleStr
