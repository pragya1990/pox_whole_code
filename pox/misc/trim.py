file1 = open('/home/mininet/pox/pox/misc/rules.txt','r')
file2 = open('/home/mininet/pox/pox/misc/rules1.txt','w+')

for line in file1:
	line = line.strip()
	file2.write(line+"\n")
file1.close()
file2.close()

