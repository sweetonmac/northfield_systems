#GPS encoding program
import os

#input file name (must be formated 1 word per line a return character at the end)
#filename = input('Enter the file name (full path eg c://Users ect): ')
filename = os.path.expanduser("~/Desktop/sampleinputdata.txt") ##input file
f = open(filename)
#outfilename = input('Enter the output file name(full path): ')
outfilename = os.path.expanduser("~/Desktop/o.txt") ##output file

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
tmp = lines[x].split('&')
date = tmp[x].split(' ')
time = date[1].split(':')
date = date[0].split('-')
date = date[0]+date[1]+date[2]
time = time[0]+time[1]+time[2]

s = memi + '&' + imsi + '&' + date + '&' + time + '&' + cpuid + '&' + tmp[1] + '&' + tmp[2] + '&' + tmp[3] + '&' + tmp[4] + '&' + tmp[5] + '&' + tmp[6] + '&' + tmp[7] + '&' + tmp[8][:-1] + '*'
o.write(s)




#loop for each line
for x in range(1,length):
    tmp2 = lines[x].split('&')
    
    ##work out time difference
    date2 = tmp2[0].split()
    time2 = date2[1].split(':')
    date2 = date2[0].split('-')
    date2 = date2[0]+date2[1]+date2[2]
    time2 = time2[0]+time2[1]+time2[2]
    datediff = str(float(date)-float(date2))
    timediff = str(float(time)-float(time2))
    s = datediff+'&'+timediff
    date = date2
    time = time2
    for y in range(1,len(tmp2)):
        s = s + '&' + str(round(float(tmp[y])-float(tmp2[y]),6))
    s = s + '*'
    tmp = tmp2
    o.write(s)
    


#close the files
o.close()
f.close()
