#GPS encoding program
import os

#input file name (must be formated 1 word per line a return character at the end)
#filename = input('Enter the file name (full path eg c://Users ect): ')
filename = os.path.expanduser("~/Desktop/o.txt") ##input file
f = open(filename)
#outfilename = input('Enter the output file name(full path): ')
outfilename = os.path.expanduser("~/Desktop/decode.txt") ##output file

memi = '0'
imsi = '1'
cpuid = '2'



#import all lines from file
lines = f.readlines()
#get length of filsampleinputdata.txte
length = len(lines)

point = []

#create new output file

o = open(outfilename,"w")

y = 0
x = 0
#buildHeader
tmp = lines[0].split('*')
tmp2 = tmp[0].split('&')
memi = tmp2[0]
imsi = tmp2[1]
date = tmp2[2]
time = tmp2[3]
cpuid = tmp2[4]
lat = tmp2[5]
lon = tmp2[6]
alt = tmp2[7]
speed = tmp2[8]
Rcount = tmp2[9]
temp = tmp2[10]
spare = tmp2[11]
spare2 = tmp2[12]

s = memi + '&' + imsi + '&' + date + '&' + time  + '&' + cpuid + '&' + lat + '&' + lon + '&' + alt + '&' + speed + '&' + Rcount + '&' + temp + '&' + spare + '&' + spare2 + '\n'
o.write(s)


for x in range(1,len(tmp)-1):
    tmp2 = tmp[x].split('&')
    date = str(float(date) - float(tmp2[0]))
    time = ("%13.6F" %(float(time) - float(tmp2[1]))).replace(' ','0')
    lat = str(float(lat) - float(tmp2[2]))
    lon = str(float(lon) - float(tmp2[3]))
    alt = str(float(alt) - float(tmp2[4]))
    speed = str(float(speed) - float(tmp2[5]))
    Rcount = str(float(Rcount) - float(tmp2[6]))
    temp = str(float(temp) - float(tmp2[7]))
    spare = str(int(float(spare) - float(tmp2[8])))
    spare2 = str(int(float(spare2)-float(tmp2[9])))
    s = memi + '&' + imsi + '&' + date + '&' + time+ '&' + cpuid + '&' + lat + '&' + lon + '&' + alt + '&' + speed + '&' + Rcount + '&' + temp + '&' + spare + '&' + spare2 + '\n'
    o.write(s)

#close the files
o.close()
f.close()
