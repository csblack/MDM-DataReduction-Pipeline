#!/usr/bin/env python

import glob, os
from pyraf import iraf
from iraf import images,noao,imred,ccdred,twodspec,longslit,apextract,onedspec
from iraf import hselect,bias,linebias,imarith,imdelete,imcopy,flatcombine,response,ccdproc,apall


######
#Copying image to current directory with new name x000.fits
######
### TO DO AT END WHEN CODE IS DONE ###


file_list = glob.glob("*.fits")
SpecCentBG_list=[]
text_file = open("data_SpecCentBG.txt","wr")

for f in file_list:
    if hselect(f,"$I","SLITID=='1.2 center'" and "DISPID=='Blue Grism'" and "naxis1=4128" and "naxis2=1016",Stdout=1):
        SpecCentBG_list.append(f)


for f in range(0,len(SpecCentBG_list)):
    if f < len(SpecCentBG_list)-1:
        text_file.write(SpecCentBG_list[f]+"\n")
    else:
        text_file.write(SpecCentBG_list[f])
        
text_file.close()


######
#Clear CCDPROC
######
ccdproc.noproc="no"
ccdproc.fixpix="no"
ccdproc.overscan="no"
ccdproc.trim="no"
ccdproc.zerocor="no"
ccdproc.darkcor="no"
ccdproc.flatcor="no"
ccdproc.illumcor="no"
ccdproc.fringecor="no"
ccdproc.readcor="no"
ccdproc.scancor="no"


######********************************************
#Reducing OSMOS 1.2 Center Slit Blue Grism Spectra
######********************************************



######
#Define Variables
######
SpecCentBG_data_list=[]
SpecCentBG_flat_list=[]
SpecCentBG_bt_list=[]
SpecCentBG_btf_list=[]
SpecCentBG_btfcr_list=[]
SpecCentBG_btfcr_comp_list=[]
SpecCentBG_btfcr_data_list=[]
SpecCentBG_forCR_list=[]
##
rdnoise = 2.5
gain = 1.1
##if Type == 'spectra':
mybias1="[4:29,5:490]"
mytrim1="[34:2064,1:508]"

mybias2="[4:29,515:1010]"
mytrim2="[34:2064,509:1014]"

mybias3="[4100:4125,5:490]"
mytrim3="[2065:4095,1:508]"

mybias4="[4100:4125,515:1010]"
mytrim4="[2065:4095,509:1014]"
##
dispax_4x1 = 1 # 1=horizontal image, 2=vertical image
##


######
#Subtract Bias
######

print 'Subtracting Bias (produces name.bt.fits) ...'
for f in SpecCentBG_list:
    temp=f.split('.')
    linebias(f,str(temp[0])+'.'+str(temp[1]) +'.1', bias=mybias1, trim=mytrim1 ,function="legendre",order=1, interactive="no")
    linebias(f,str(temp[0])+'.'+str(temp[1]) +'.2', bias=mybias2, trim=mytrim2 ,function="legendre",order=1, interactive="no")
    linebias(f,str(temp[0])+'.'+str(temp[1]) +'.3', bias=mybias3, trim=mytrim3 ,function="legendre",order=1, interactive="no")
    linebias(f,str(temp[0])+'.'+str(temp[1]) +'.4', bias=mybias4, trim=mytrim4 ,function="legendre",order=1, interactive="no")
    g=str(temp[0])+'.'+str(temp[1])+'.bt'+'.fits'

    imarith(f+'[34:4095,1:1014]','*',1.0 ,g)
    print 'Making final image...'

    f1=str(temp[0])+'.'+str(temp[1]) +'.1'+'.fits'
    f2=str(temp[0])+'.'+str(temp[1]) +'.2'+'.fits'
    f3=str(temp[0])+'.'+str(temp[1]) +'.3'+'.fits'
    f4=str(temp[0])+'.'+str(temp[1]) +'.4'+'.fits'
    imcopy(f1,g+'[1:2030,1:508]')
    imcopy(f2,g+'[1:2030,509:1014]')
    imcopy(f3,g+'[2031:4061,1:508]')
    imcopy(f4,g+'[2031:4061,509:1014]')

    print 'Deleting sections ...'
    imdelete(f1)
    imdelete(f2)
    imdelete(f3)
    imdelete(f4)
    SpecCentBG_bt_list.append(g)
    print 'Next Image'

for f in SpecCentBG_bt_list:
    if hselect(f,"$I","LAMPS!='Flat'",Stdout=1):
        SpecCentBG_data_list.append(f)

text_file1 = open("data.bt_SpecCentBG.txt","wr")
text_file2 = open("data.btf_SpecCentBG.txt","wr")
for f in range(0,len(SpecCentBG_data_list)):
    temp=SpecCentBG_data_list[f].split('.')
    SpecCentBG_btf_list.append(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'f'+'.fits')
    if f < len(SpecCentBG_data_list)-1:
        text_file1.write(SpecCentBG_data_list[f]+"\n")
        text_file2.write(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'f'+'.fits'+"\n")
        
    else:
        text_file1.write(SpecCentBG_data_list[f])
        text_file2.write(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'f'+'.fits')
        
text_file1.close()
text_file2.close()

######
#Combining/Normalizing Flats
######
print "Combining Flats (produces Flat) ..."   
for f in SpecCentBG_bt_list:
    if hselect(f,"$I","LAMPS=='Flat'",Stdout=1):
        SpecCentBG_flat_list.append(f)

text_file = open("flat_SpecCentBG.txt","wr")
for f in range(0,len(SpecCentBG_flat_list)):
    if f < len(SpecCentBG_flat_list)-1:
        text_file.write(SpecCentBG_flat_list[f]+"\n")
    else:
        text_file.write(SpecCentBG_flat_list[f])
        
text_file.close()


#for f in range(0,len(SpecCentBG_flat_list)):
flatcombine("@%s.txt" %'flat_SpecCentBG',output='Flat', combine="median", reject="avsigclip", gain=gain, rdnoise=rdnoise)

print "Normalize Flat (produces Flat.n) ..."
if hselect('Flat',"$I","naxis1=3166" and "naxis2=1014",Stdout=1):
    longslit.dispaxis = dispax_4x1


while True:
    response(calibration='Flat', normalization='Flat',response='Flat.n',interactive='yes',function='spline3')
    while True:
        ans=raw_input("Take a look at Flat.n.  Are you happy with it? ")
        if (ans == 'yes') or (ans == 'y'):
            break
        elif (ans == 'no') or (ans == 'n'):
            os.remove("Flat.n.fits")
            break
        elif (ans != 'no') or (ans != 'n') or (ans != 'yes') or (ans != 'y'):
            print "yes or no"
    if (ans == 'yes') or (ans == 'y'):
            break 

#display('Flat.n')

######
#Divides by Normalized Flat
######
print "Dividing Flat (produces name.btf.fits)"
#ccdproc("@%s.txt" %'data.bt_SpecCentBG',output="@%s.txt" %'data.btf_SpecCentBG',flatcor='yes',flat='Flat.n')
imarith("@%s.txt" %'data.bt_SpecCentBG', '/', "%s" %'Flat.n',"@%s.txt" %'data.btf_SpecCentBG')



######
#Remove Cosmic Rays using LA COSMIC
######

#Removes Comp Lamps from CR reduce
for f in SpecCentBG_btf_list:
    if hselect(f,"$I","LAMPS=='OFF'",Stdout=1):
        SpecCentBG_forCR_list.append(f)

text_file = open("data.btf_Forcr_SpecCentBG.txt","wr")
for f in range(0,len(SpecCentBG_forCR_list)):
    temp=SpecCentBG_forCR_list[f].split('.')
    if f < len(SpecCentBG_forCR_list)-1:
        text_file.write(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'.fits'+"\n")
        
    else:
        text_file.write(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'.fits')
        
text_file.close()

        
print "Running LA Cosmic (produces name.btf.cr.fits)"
text_file = open("data.btf.cr_SpecCentBG.txt","wr")
for f in range(0,len(SpecCentBG_forCR_list)):
    temp=SpecCentBG_forCR_list[f].split('.')
    if f < len(SpecCentBG_forCR_list)-1:
        text_file.write(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'.cr'+'.fits'+"\n")
        
    else:
        text_file.write(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'.cr'+'.fits')
        
text_file.close()

# The following two lines are only needed as cosmic.py is not in this directory nor in the python path.
# They would not be required if you copy cosmics.py in this directory.
import sys
sys.path.append("/Users/Hogan/cosmics.py_0.4") # The directory that contains cosmic.py


import cosmics

text_file = open("data.btf_Forcr_SpecCentBG.txt","r")
lines=text_file.readlines()

# Read the FITS :
for l in lines:
    array, header = cosmics.fromfits(l)
    # array is a 2D numpy array
    
    # Build the object :
    c = cosmics.cosmicsimage(array, gain=gain, readnoise=rdnoise, sigclip = 5.0, sigfrac = 0.3, objlim = 5.0)
    # There are other options, check the manual...

    # Run the full artillery :
    c.run(maxiter = 4)
    temp=l.split('.')
    #SpecCentBG_btfcr_list.append(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'.cr'+'.fits')
    # Write the cleaned image into a new FITS file, conserving the original header :
    cosmics.tofits(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'.cr'+'.fits', c.cleanarray, header)

    # If you want the mask, here it is :
    cosmics.tofits("mask.fits", c.mask, header)
    # (c.mask is a boolean numpy array, that gets converted here to an integer array)

"""
######
#Running Apall
######

print "Running Apall (produces name.btf.crap.fits)"
text_file1 = open("data.btf.cr_SpecCentBG.txt","r")
lines=text_file1.readlines()

for l in lines:
    if hselect(l.rstrip('\n'),"$I","LAMPS=='Xe'",Stdout=1) or hselect(l.rstrip('\n'),"$I","LAMPS=='Ar'",Stdout=1) or  hselect(l.rstrip('\n'),"$I","LAMPS=='Ne Hg'",Stdout=1):
        SpecCentBG_btfcr_comp_list.append(l.rstrip('\n'))
    elif hselect(l.rstrip('\n'),"$I","LAMPS=='OFF'",Stdout=1):
        SpecCentBG_btfcr_data_list.append(l.rstrip('\n'))

text_file2 = open("data.btf.crap_SpecCentBG.txt","wr")
for l in range(0,len(lines)):
    temp=lines[l].rstrip('\n').split('.')
    if l < len(lines)-1:
        text_file2.write(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'.'+str(temp[3])+'ap'+'.fits'+"\n")        
    else:
        text_file2.write(str(temp[0])+'.'+str(temp[1])+'.'+str(temp[2])+'.'+str(temp[3])+'ap'+'.fits')
text_file1.close()        
text_file2.close()

ans=raw_input("To run Apall you need Line value for spectra (ie 320) and Background range (ie -20:10, 10:20).  Press enter when ready to procede: ")
line=raw_input("What is your Line value? X-value for Horizontal spectra Y-value for Verticle spectra ")
bkgnd=raw_input("What is your Background range? Enter as W:X,Y:Z ")

apall.apertures='1'
apall.format='multispec'
apall.references=""
apall.profiles=""
apall.interactive='yes'
apall.find='yes'
apall.recenter='no'
apall.resize='no'
apall.edit='yes'
apall.trace='yes'
apall.fittrace='yes'
apall.extract='yes'
apall.extras='no'
apall.review='no'
apall.line=line
apall.nsum='-20'
apall.b_sample=bkgnd
apall.background='median'
apall.weights='variance'

apall('n2.0064.btf.cr',output='n2.0064.btf.crap')

"""
print "\n"+"Done!"
