from twisted.internet import reactor, protocol

class HeadClient( protocol.Protocol ):

  def connectionMade( self ):
    self.transport.write( "GET_ADDRESSMAP" )

  def dataReceived( self, data ):
    print "Received: "

  def connectionLost( self, reason ):
    print "Connection lost."

class HeadFactory( protocol.ClientFactory ):
  protocol = HeadClient

  def clientConnectionFailed( self, connector, reason ):
    print "Connection failed - goodbye!"
    reactor.stop()

  def clientConnectionLost( self, connector, reason ):
    print "Connection lost - goodbye!"
    reactor.stop()

class Head( protocol.Protocol ):

  def dataReceived( self, data ):
    print "Received command: ", data

class Unit( protocol.Protocol ):

  def dataReceived( self, data ):
    print "Received data: ", data

def main( address, port )
  # Start a client to talk to the head unit
  f = HeadFactory()
  reactor.connectTCP( address, port, f )

  # Start a server to listen to commands from head unit
  head_factory = protocol.ServerFactory()
  head_factory.protocol = ???
  reactor.listenTCP( 8000, head_factory )

  # Start a server to receive inputs from units
  unit_factory = protocol.ServerFactory()
  unit_factory.protocol = ???
  reactor.listenTCP( 8001, unit_factory )

  # Start a client to send outputs
  # Connection needs to be done when the address is known
  # Should this be done within the node's output function?
  # Probably

  # Run the socks
  reactor.run()

  # Kill all the socks
  # HOW?

if __name__ == "__main__":
  ( address, port ) = argv[1], argv[2]
  main( address, port )
