# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 14:38:24 2014
This module provides function for extracting bounding box coordinates and the confidence of OCR for each of those bounding boxes. Saves file at the same location with <name>_AL.csv
@author: guptaa
"""
import bs4
import numpy as np
def parseHOCR(fileName):
    soup = bs4.BeautifulSoup(open(fileName,'r')) #51150019_1 - test 379_1 ; 2271337_13 - test id=6, 380_13; 45949734_1 , 45444878_5, 53211844_160 - 132 and 160; 48898051_301 131 and 301 ; 45509238_1 - 128 and 1; 45977751_1 128 and 
    pageInfo = soup.find_all('div',class_="ocr_page")# id='page_1'
    if pageInfo.__len__()>1:
        f_log = open("multiple-page-errors.txt","a") 
        f_log.write("\nMultiple page error : Image file path- %s hOCR file path- %s. Processing first page only.\n"%(pageInfo[0]["title"].split(";")[0],fileName))
        f_log.close()
    pageInfo = pageInfo[0];
    soup=pageInfo 
    t_x,t_y,pageWidth,pageHeight = pageInfo["title"].split(';')[1].split('bbox ')[1].split(' ')
    pageWidth = float(pageWidth)
    pageHeight = float(pageHeight)
    
    allSpanTags = [];
    allSpanTags=soup.find_all("span",class_="ocrx_word")
    #print allSpanTags.__len__()
    #print allSpanTags.__len__()
    wordInfo = np.ndarray((allSpanTags.__len__(),9))
    wordInfo1 = {};
    wordInfoNon_Scaled = np.ndarray((allSpanTags.__len__(),9))
    count=0;
    for val in allSpanTags:
        splitList = val["title"].split(';')
        x1,y1,x2,y2 = splitList[0].split('bbox ')[1].split(' ')
        w_conf = float(splitList[1].split('x_wconf ')[1])/100
        word_id = int(val["id"].split("word_")[1])
        #print val
        lenStr=[unicode(s).encode("utf-8") for s in val.contents];
        if len(lenStr)!=0:
            lenStr=len(lenStr[0]);
        else:
            lenStr = 0;
       
        #print lenStr
        wordInfoNon_Scaled[count,:]= np.array([word_id, int(x1),int(y1),int(x2),int(y2),abs(int(y2) - int(y1)), abs(int(x2) - int(x1)),w_conf,lenStr])
        x1 = (int(x1)/pageWidth)
        y1 = (1 - (int(y1)/pageHeight))
        x2 = (int(x2)/pageWidth)
        y2 = (1 - (int(y2)/pageHeight))
        height = (abs(y2 - y1))
        width = (abs(x2 - x1))
        #print np.float16(np.array([word_id, x1,y1,x2,y2,height, width,w_conf])) 
        #print word_id-1,(np.array([word_id,]))        
        
        wordInfo[count,:]= (np.array([word_id, x1,y1,x2,y2,height, width,w_conf,lenStr]))
        #print [unicode(s).encode("utf-8") for s in val.contents]
        #print [len(s) for s in val.contents]
        count = count+1;
    wordInfo1[1]=wordInfo
    wordInfo1[2]=pageWidth
    wordInfo1[3]=pageHeight
    return wordInfo1

if __name__=="__main__":
    props=parseHOCR('E:/EMOP/Data/679/118125/53211819_135_IDHMC.xml')
    print props
    