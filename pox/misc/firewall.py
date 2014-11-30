'''
Coursera:
- Software Defined Networking (SDN) course
-- Module 4 Programming Assignment

Professor: Nick Feamster
Teaching Assistant: Muhammad Shahbaz
'''

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
import re
''' Add your imports here ... '''

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree
from collections import namedtuple

log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]  

''' Add your global variables here ... '''



class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")
	core.openflow_discovery.addListeners(self)

    def _handle_ConnectionUp(self,event):
	msg=of.ofp_packet_out()
	msg.match = of.ofp_match()
	msg.match.in_port = of.OFPP_NONE
	msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
	event.connection.send(msg)
	print "handle connection up"
    
    def _handle_PacketIn (self, event):
    
    	def install_firewall(event,packet):
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match()
	    msg.match.dl_src=EthAddr('00:00:00:00:00:01')
	    msg.match.dl_dst=EthAddr('00:00:00:00:00:02')
            event.connection.send(msg)
	    print msg	  
	    print "install_firewall"       

	print "HANDLE *************" 
	packet = event.parsed
	fp = open('/home/mininet/pox/pox/misc/firewall-policies.csv', 'r')
        lines = fp.readlines()
        fp.close()
        counter = 0
        for line in lines:
                counter = counter + 1
		if counter==1:
			continue
		words = re.split(',',line)
		print words
		h1 = words[1]
		h2 = words[2].strip()
		print h1
		print h2
		install_firewall(event,packet)
		    
        #log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))
      
def launch ():
    '''
    Starting the Firewall module
    '''
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()
    core.registerNew(Firewall)
