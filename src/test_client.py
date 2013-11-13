from twisted.internet import reactor, protocol

class NodeClient( protocol.Protocol ):

  def connectionMade( self ):
    data = (1, 35, 14.32)
    msg = ",".join( str(datum) for datum in data )
    self.transport.write( msg )

  def dataReceived( self, data ):
    print "Received: "
    data = data.split( "," )
    for heading, data in zip( ("GID", "Time", "Voltage"), data ):
      print "%s: %2.2f" % (heading, float(data) )
    self.transport.loseConnection()

  def connectionLost( self, reason ):
    print "Connection lost."

class NodeFactory( protocol.ClientFactory ):
  protocol = NodeClient

  def clientConnectionFailed( self, connector, reason ):
    print "Connection failed - goodbye!"
    reactor.stop()

  def clientConnectionLost( self, connector, reason ):
    print "Connection lost - goodbye!"
    reactor.stop()

def main():
  f = NodeFactory()
  reactor.connectTCP( "localhost", 8000, f )
  reactor.run()

if __name__ == "__main__":
  main()
