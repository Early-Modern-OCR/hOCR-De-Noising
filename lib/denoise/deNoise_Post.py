# -*- coding: utf-8 -*-
#import sys
#Add search path to 

#sys.path.append('/home/anshulg/PythonPackages/lib/python')

import bs4
import numpy as np;
#import matplotlib.pyplot as pl
import peaks_find as pks
import optparse as parser_opt
import datetime
import time

    
def deNoise(filePath,fileName):
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
    pageInfo = soup.find('div',id='page_1',class_="ocr_page")
    t_x,t_y,pageWidth,pageHeight = pageInfo["title"].split(';')[1].split('bbox ')[1].split(' ')
    pageWidth = float(pageWidth)
    pageHeight = float(pageHeight)
    
    allSpanTags=soup.find_all("span",class_="ocrx_word")
    
    wordInfo = np.float16(np.ndarray((allSpanTags.__len__(),8)))
    wordInfoNon_Scaled = np.ndarray((allSpanTags.__len__(),8))
    for val in allSpanTags:
        splitList = val["title"].split(';')
        x1,y1,x2,y2 = splitList[0].split('bbox ')[1].split(' ')
        w_conf = float(splitList[1].split('x_wconf ')[1])/100
        word_id = int(val["id"].split("word_")[1])
        wordInfoNon_Scaled[word_id-1,:]= np.array([word_id, int(x1),int(y1),int(x2),int(y2),abs(int(y2) - int(y1)), abs(int(x2) - int(x1)),w_conf])
        x1 = np.float16(int(x1)/pageWidth)
        y1 = np.float16(1 - (int(y1)/pageHeight))
        x2 = np.float16(int(x2)/pageWidth)
        y2 = np.float16(1 - (int(y2)/pageHeight))
        height = np.float16(abs(y2 - y1))
        width = np.float16(abs(x2 - x1))
        wordInfo[word_id-1,:]= np.float16(np.array([word_id, x1,y1,x2,y2,height, width,w_conf])) 
        
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
        area_descend_cumsum=np.float16(np.cumsum(area_descend)/np.sum(area_descend))
        areaThInd = area_descend_cumsum>=preDeNoiseParameters[3]
        if np.any(areaThInd):
            areaTh=area_descend[areaThInd][0]
            ixAreaFilter = area_bboxes>areaTh
            finalFilter = tempFilter & ixAreaFilter
        else:
            finalFilter = tempFilter
        preFilteredData = wordInfo[finalFilter,:]
        
        # Calculate page bounds after preDenoising
        max_x = np.float16(np.max(wordInfo[finalFilter,3]));
        max_y = np.float16(np.max(wordInfo[finalFilter,2]));
        min_x = np.float16(np.min(wordInfo[finalFilter,1]));
        min_y = np.float(np.min(wordInfo[finalFilter,4]));
        
        #Number of bounding boxes after preDenoising
        numBbox = np.size(np.ix_(finalFilter))
        
        # Page Splitting algorithm
        # 1. x_Intersection profile
        xPointsUp = np.float16(np.arange(min_x,max_x,np.float16((max_x-min_x)/1000)))#min_x:(max_x-min_x)/1000:max_x;
        stepFromTop=np.float16(0.2*(max_y-min_y)) # range to consider. Removing top and bottom 20% bboxes
        indexToConsider = preFilteredData[:,2]<np.float16((max_y-stepFromTop))
        indexToConsiderTemp = preFilteredData[:,4]>np.float16((min_y+stepFromTop))
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
        prcOutputMovAvg = np.float16(np.percentile(intersectionCountProfile,80))
        negIntersectionCountProfile = -np.float16(intersectionCountProfile/prcOutputMovAvg);
        
        # Find CutPoints
        #NOTE : For future work below code can be generalized to handle any number of columns. Right now it can handle upto 4 columns on a page image
    
        max_,min_ = pks.peakdetect(negIntersectionCountProfile,lookahead=150,delta=np.diff(negIntersectionCountProfile).max() * 2)
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
            cutPoints[0]=np.float16(np.mean(100*tempCutPoints))/100.0
        else:
            ix_ = calculateCutPointIx(acceptedPeaks,np.arange(199,399))
            if ix_!=-1:
                cutPoints[0] = xPointsUp[ix_]
            
            
        if np.any(negIntersectionCountProfile[400:599]==0):
            temp = np.arange(400,599)
            tempCutPoints=xPointsUp[temp[negIntersectionCountProfile[400:599]==0]];
            cutPoints[1] =np.float16(np.mean(100*tempCutPoints))/100.0
        else:
            ix_ = calculateCutPointIx(acceptedPeaks,np.arange(400,599))
            if ix_!=-1:
                cutPoints[1] = xPointsUp[ix_]
    
        if np.any(negIntersectionCountProfile[600:799]==0):
            temp = np.arange(600,799)
            tempCutPoints=xPointsUp[temp[negIntersectionCountProfile[600:799]==0]];
            cutPoints[2] = np.float16(np.mean(100*tempCutPoints))/100.0
        else:
            ix_ = calculateCutPointIx(acceptedPeaks,np.arange(600,799))
            if ix_!=-1:
                cutPoints[2] = xPointsUp[ix_]
        if (np.size(np.ix_(negIntersectionCountProfile==0))/float(np.size(negIntersectionCountProfile)))>=0.5:
            temp = np.arange(399,599)
            cutPoints[2] =np.float16(np.mean(100*tempCutPoints))/100.0
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
            else:
                D_max = 0;
                medianHeight = 0;
                iqrHeight = 1.0
            
            confTemp = wordInfo[actualIndexToConsider,7];
            iter_ = 0;
            count_ = 0;
            numPrevError = -999;
            numCurrentError = 0;
            while((np.size(np.ix_(finalFilterTemp!=prevfinalFilterTemp)) > 1) and (iter_< max_iter) and (count_<3)): 
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
        for word_id in range(0,np.size(wordInfo[:,0])):
            temp = soup.find("span",class_="ocrx_word",id="word_%d"%(wordInfo[word_id,0]))
            temp['title'] = "%s; pred %d; predConf %.4f"%(temp['title'],MLFilter[word_id],confVal[word_id])
        
        f = open("%s%s_SEASR.xml"%(filePath,fileName.replace('.xml','')),'w')
        f.write(soup.encode())
        f.close()
        
        toDel = np.ix_(MLFilter==0)[0]
        soup1 = bs4.BeautifulSoup(open(fileName1))
        for word_id in range(0,np.size(toDel)):
            temp = soup1.find("span",class_="ocrx_word",id="word_%d"%(wordInfo[toDel[word_id],0]))
            temp.extract()
        
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
        
        toDel = np.ix_(MLFilter==0)[0]
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
    parser.add_option('-b', '--batchNumber',action="store", dest="batchNum",help="Current Batch Number", default="Not Given")
    options, args = parser.parse_args()
    f = open("%s_logFile_PSI_PostProcessing.txt"%(options.fileName.replace('.xml','')),'a')
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S');  
#    try:
    logError(f,"\n%s : Processing '%s'..."%(st,options.fileName))
    deNoise(options.filePath,options.fileName)
    #deNoise('C:\Users\guptaa.JAEN\Google Drive\EMOP\PythonImplDenoise\DeNoise','1.xml')
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'); 
    logError(f,"\n%s : Processing Completed."%(st))
#    except Exception, e:      
#        logError(f,"\nProcessing failed with error : %s"%(e))
#    f.close()
        
        
            


    
    


