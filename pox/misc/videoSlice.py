'''
Coursera:
- Software Defined Networking (SDN) course
-- Network Virtualization

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

from pox.core import core
from collections import defaultdict

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree

from pox.lib.Rule import Shared

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os

log = core.getLogger()


class VideoSlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)

        # Adjacency map.  [sw1][sw2] -> port from sw1 to sw2
        self.adjacency = defaultdict(lambda:defaultdict(lambda:None))

        '''
        The structure of self.portmap is a four-tuple key and a string value.
        The type is:
        (dpid string, src MAC addr, dst MAC addr, port (int)) -> dpid of next switch
        '''

        '''self.portmap = {
        # h1 <-- port 80 --> h3
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-03',

                        #  """ Add your mapping logic here"""
                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-04',

                        ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-01',

                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-03',
                            #port 22
                         ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                          EthAddr('00:00:00:00:00:03'), 22): '00-00-00-00-00-02',
                          
                         ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:01'),
                          EthAddr('00:00:00:00:00:03'), 22): '00-00-00-00-00-04',
                          
                         ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                          EthAddr('00:00:00:00:00:01'), 22): '00-00-00-00-00-02',
                          
                         ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:03'),
                          EthAddr('00:00:00:00:00:01'), 22): '00-00-00-00-00-01',
                         
                         #h2--h4
                        
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-03',
                            
                         ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:02'),
                          EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-04',
                          
                         ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                          EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-03',
                          
                         ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:04'),
                          EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-01',
        
        
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 22): '00-00-00-00-00-02',

                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 22): '00-00-00-00-00-04',

                        ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:02'), 22): '00-00-00-00-00-01',

                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:02'), 22): '00-00-00-00-00-02',
                        
                        #h1-h4
                        
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-03',
                            
                         ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:01'),
                          EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-04',
                          
                         ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                          EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-03',
                          
                         ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:04'),
                          EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-01',
                         
                         ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                          EthAddr('00:00:00:00:00:04'), 22): '00-00-00-00-00-02',
                          
                         ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:01'),
                          EthAddr('00:00:00:00:00:04'), 22): '00-00-00-00-00-04',
                          
                         ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                          EthAddr('00:00:00:00:00:01'), 22): '00-00-00-00-00-02',
                          
                         ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:04'),
                          EthAddr('00:00:00:00:00:01'), 22): '00-00-00-00-00-01',
                         
                         #h2-h3
                         
                         ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                          EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-03',
                          
                         ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:02'),
                          EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-04',
                          
                         ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                          EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-03',
                          
                         ('00-00-00-00-00-03', EthAddr('00:00:00:00:00:03'),
                          EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-01',
                         
                         ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                          EthAddr('00:00:00:00:00:03'), 22): '00-00-00-00-00-02',
                          
                         ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:02'),
                          EthAddr('00:00:00:00:00:03'), 22): '00-00-00-00-00-04',
                          
                         ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                          EthAddr('00:00:00:00:00:02'), 22): '00-00-00-00-00-02',
                          
                         ('00-00-00-00-00-02', EthAddr('00:00:00:00:00:03'),
                          EthAddr('00:00:00:00:00:02'), 22): '00-00-00-00-00-01',

                         
                         
                         
                         
                        }
	'''
	self.portmap = {}
	fp = open('/home/mininet/pox/pox/misc/rules.txt', 'r')
	lines = fp.readlines()
	fp.close()	
	counter = 0
	for line in lines:
		line = line.strip()
		counter = counter + 1
		words = line.split(',')
		print line
		if words[0].strip() == "VideoRule":
			t = ()
			t = t + (words[1].strip(),EthAddr(words[2].strip()),EthAddr(words[3].strip()),int(words[4].strip()))
			self.portmap[t] = words[5].strip()
			print self.portmap[t]
 	

    def _handle_LinkEvent (self, event):
        l = event.link
        sw1 = dpid_to_str(l.dpid1)
        sw2 = dpid_to_str(l.dpid2)

        log.debug ("link %s[%d] <-> %s[%d]",
                   sw1, l.port1,
                   sw2, l.port2)

        self.adjacency[sw1][sw2] = l.port1
        self.adjacency[sw2][sw1] = l.port2


    def _handle_PacketIn (self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """
        packet = event.parsed
        tcpp = event.parsed.find('tcp')
	print "HANDLE *****"
	def install_firewall(event,packet,h1,h2):
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match()
	    print h1
	    print h2
            msg.match.dl_src=EthAddr(h1)
            msg.match.dl_dst=EthAddr(h2)
            event.connection.send(msg)

        def install_fwdrule(event,packet,outport):
            msg = of.ofp_flow_mod()
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.match = of.ofp_match.from_packet(packet, event.port)
            msg.actions.append(of.ofp_action_output(port = outport))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        def forward (message = None):
            this_dpid = dpid_to_str(event.dpid)
	    if Shared.FlowQoS == 1:
	        #print("Flows have changed, reading file")
		self.portmap = {}
		fp = open('/home/mininet/pox/pox/misc/rules.txt', 'r')
		lines = fp.readlines()
		fp.close()	
		counter = 0
		for line in lines:
		    counter = counter + 1
		    words = line.split(',')
		    print words[0]
		    if words[0].strip() == "VideoRule":
		        t = ()
			t = t + (str(words[1].strip()),EthAddr(words[2].strip()),EthAddr(words[3].strip()),int(words[4].strip()))
			print "%%%%%%%% VIDEORUL"
			self.portmap[t] = str(words[5].strip())
			print self.portmap[t]
		   	for keys,values in self.portmap.items():
				print str(keys) + ":" + str(values)  
				#print self.portmap
	    			print "counter: " + str(counter)
	    		
	        if packet.dst.is_multicast:
			print "Destination multicast, flooding the packet."
               	 	flood()
                	return
            	else:
                   	log.debug("Got unicast packet for %s at %s (input port %d):",
                        packet.dst, dpid_to_str(event.dpid), event.port)
			key_map = ()
                	try:
				#  """ Add your logic here""""
				key_map = (this_dpid, packet.src, packet.dst, packet.find('tcp').dstport)
				if not self.portmap.get(key_map):
					key_map = (this_dpid, packet.src, packet.dst, packet.find('tcp').srcport)
					if not self.portmap.get(key_map):
						raise AttributeError
					print "FOUND: " + str(key_map)
					next_dpid = self.portmap[key_map]
					install_fwdrule(event,packet,self.adjacency[this_dpid][next_dpid])
				except AttributeError:
                    			log.debug("packet type has no transport ports, flooding")
		    			print "FLOOD: " + str(key_map)
                    			# flood and install the flow table entry for the flood
                    			install_fwdrule(event,packet,of.OFPP_FLOOD)
		 
		        '''elif words[0].strip() == "FirewallRule":
                	words = re.split(',',line)
                	print words
                	h1 = words[1]
                	h2 = words[2].strip()
                	print h1
                	print h2
                	install_firewall(event,packet)                   
		     	'''
        # flood, but don't install the rule
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        forward()


    def _handle_ConnectionUp(self, event):
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)
	#msg = of.ofp_flow_mod()
	#msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
	#event.connection.send(msg)
    

def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Video Slicing module
    '''
    core.registerNew(VideoSlice)
