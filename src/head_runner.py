from twisted.internet import reactor, protocol
from twisted.internet.defer import DeferredLock
from collections import defaultdict

node_to_gid_map = {}
inputs = {}
outputs = {}

class UnitClient( protocol.Protocol ):

  def connectionMade( self ):
    global node_to_gid_map, outputs


    self.transport.write( "#".join( ( "MAP",     
                                      str( node_to_gid_map ),
                                      "OUTPUTS",
                                      str( outputs ) ) ) )
    self.transport.loseConnection()

  def connectionLost( self, reason ):
    print "Connection closed."

class UnitClientFactory( protocol.ClientFactory ):
  protocol = UnitClient

  def clientConnectionFailed( self, connector, reason ):
    print "Conn failed."

  def clientConnectionLost( self, connector, reason ):
    print "Conn lost."

class HeadClient():

  client = UnitClientFactory()

  def send_network_info( self, unit_list ):
    for ( ip, port ) in unit_list:
      reactor.connectTCP( ip, int( port ), HeadClient.client )

class Head( protocol.Protocol ):

  unit_list = []
  next_gid = 0
  _lock = DeferredLock()
  head_client = HeadClient()

  def __init__( self ):
    self.f = { 'CONNECT': self._connect }
    Head._lock = DeferredLock()

  def dataReceived( self, data ):
    tokens = data.split( "," )
    command, args = tokens[0], tokens[1:]
    return Head._lock.run( self.f[command], args )

  def _connect( self, args ):
    global node_to_gid_map

    node_type, port, num_nodes = args[0], args[1], int( args[2] )
    current_gid = Head.next_gid
    Head.next_gid += num_nodes
    ip = self.transport.getPeer().host
    print "Server: connecting node with ip=%s and port=%s" % ( ip, port )

    self.transport.write( str( current_gid ) )
    Head.unit_list.append( ( ip, port ) )
    for gid in range( current_gid, current_gid + num_nodes ):
      node_to_gid_map[gid] = ( ip, port )
      if node_type == "INPUT":
        inputs[gid]  = ( ip, port )
      else:
        outputs[gid] = ( ip, port )

    self.transport.loseConnection()

  def connectionLost( self, reason ):
    global inputs, outputs

    if ( len( Head.unit_list ) == 10 ):
      Head.head_client.send_network_info( Head.unit_list )

def main():
  print "Starting up the spiking neural network head unit..."

  head_factory = protocol.ServerFactory()
  head_factory.protocol = Head
  reactor.listenTCP( 8000, head_factory )
  
  reactor.run()

if __name__ == "__main__":
  main()
