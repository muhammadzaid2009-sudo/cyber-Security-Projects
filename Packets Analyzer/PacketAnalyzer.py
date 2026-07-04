from scapy.all import *

file = rdpcap("capture.pcapng")
# check every packet by its index you can change the index to check different packet numbers
f = file[0]
print(f.show())


#file = file.show()
#print(file)
