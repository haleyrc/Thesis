import sys
from twisted.internet import reactor, protocol
from collections import defaultdict
from snn.snn import *

SRV_PORT = 8001
START_GID = 0
NODE_NUM = 0
NODE_TYPE = "INPUT"
node_to_gid_map = defaultdict( list )
neurons = []
spike = SpikeDetector()
poissons = []
generators = []
el = EntityList()

class HeadClient( protocol.Protocol ):

  def connectionMade( self ):
    data = ",".join( str(token) for token in 
        [ "CONNECT", NODE_TYPE, SRV_PORT, NODE_NUM ] )
    self.transport.write( data )

  def dataReceived( self, data ):
    global neurons, spike, poissons, generators, el, NODE_TYPE

    # xxx eval is pretty unsafe in production
    START_GID = int( data )

    if NODE_TYPE == "INPUT":
      for i in range( START_GID, START_GID + NODE_NUM ):
        print "Staring node with gid:", i
        IAFNeuron.next_id = START_GID
        neurons.append( IAFNeuron( threshold_voltage = -55 ) )
        neurons[i].to_file = False
        neurons[i].to_screen = False
        generators.append( ACGenerator( amplitude = 500., frequency = 2. ) )
        generators[i].connect( neurons[i] )
        poissons.append( PoissonGenerator( randint( 10, 100 ) ) )
        poissons.append( PoissonGenerator( randint( 10, 100 ) ) )
        convergentConnect( 
            [poissons[2*i], poissons[2*i+1]], neurons[i], [1.2, -1.0] )
        poissons[2*i  ].connect( neurons[i] )
        poissons[2*i+1].connect( neurons[i] )
        neurons[i].connect( spike )

      el.add( generators )
      el.add( poissons )
      el.add( neurons )

    else:
      output_neuron = IAFNeuron( threshold_voltage = -55 )
      output_neuron.to_file = False
      output_neuron.to_screen = False
      convergentConnect( neurons, output_neuron, 
          [( val + 1 ) * 30 for val in range( network_size )] )
      output_neuron.connect( spike )
      el.add( output_neuron )
      el.add( spike )

    self.transport.loseConnection()

  def connectionLost( self, reason ):
    print "Connection closed."

class HeadClientFactory( protocol.ClientFactory ):
  protocol = HeadClient

  def clientConnectionFailed( self, connector, reason ):
    print "Conn failed."
    reactor.stop()

  def clientConnectionLost( self, connector, reason ):
    print "Conn lost."

class Unit( protocol.Protocol ):

  def __init__( self ):
    self.data_handlers = { 'TICK'    : self._tick,
                           'INPUT'   : self._input,
                           'OUTPUTS' : self._convergentConnect,
                           'MAP'     : self._map    }
  
  def dataReceived( self, data ):
    split_data = data.split( '#' )
    for i in xrange( 0, len( split_data ), 2 ):
      command, data = split_data[i], split_data[i+1]
      self.data_handlers[ command ]( data )

  def _convergentConnect( self, data ):
    if NODE_TYPE == "INPUT":
      print "Input node, needs connecting"
    else:
      print "Output node"

  def _map( self, data ):
    global node_to_gid_map

    node_to_gid_map = eval( data )
    print "Unit listening on port",  SRV_PORT, 
    print "rec'd data len:", len( node_to_gid_map )

  def _tick( self, data ):
    pass

  def _input( self, data ):
    pass

def main() :
  global NODE_NUM, SRV_PORT, NODE_TYPE

  IP_ADDRESS = sys.argv[4]
  SRV_PORT = sys.argv[3]
  NODE_NUM = int( sys.argv[2] )
  NODE_TYPE = sys.argv[1]

  print "\nStarting an %s type node..." % NODE_TYPE 
  print "Connecting to the head unit..."
  client = HeadClientFactory()
  reactor.connectTCP( IP_ADDRESS, 8000, client )

  unit_server = protocol.ServerFactory()
  unit_server.protocol = Unit
  reactor.listenTCP( int( SRV_PORT ), unit_server )

  reactor.run()

if __name__ == "__main__":
  main()
