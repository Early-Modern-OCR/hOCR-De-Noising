Files:

1) parseOCR.py is the module which takes a hOCR(filtered by deNoising and created with _IDHMC name) and generates a numpy 2d array of coordinates of word bounding boxes.

2) peaks_find.py : Is a peak picking code. It has many functions in it. I am using it for finding peaks in the intersection profile.

3) multiColDetect.py: It is the main module which contains multiColumnDetect function. It has following dependencies:
	a) Need parseOCR.py module
	b) Need peaks_find.py module.
In order to link the above mentioned module, you need to append the path of the source folder where these python modules will be placed. You can add the path using following: 
import sys
sys.path.append("<path_to_source_folder>")

This function performs both the function: 1) column detection and skew angle estimation.

The outputs of this function are :

1) multiColPoints : It is a string of the form : 1800,4000,6000 
This means that the x coordinate of the end of the first column is located at 1800 , for second column end is located at 4000 and so on.

2) skewAngleStr : It is a strinf of the form: -1.0,2.0, 

These numbers are the skew angle in degrees. 

The first value -1.0 is the skew angle for the first page/column of the image and 2.0 is the skew angle for the second page/column of the image.

In order to correct the page you need to rotate the page image by -ve of its skew angle.



