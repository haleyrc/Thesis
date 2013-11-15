from twisted.internet import reactor, protocol

class HeadClient( protocol.Protocol ):

  def connectionMade( self ):
    pass

  def dataReceived( self, data ):
    pass

  def connectionLost( self, reason ):
    pass

class HeadClientFactory( protocol.ClientFactory ):
  protocol = HeadClient

  def clientConnectionFailed( self, connector, reason ):
    pass

  def clientConnectionLost( self, connector, reason ):
    pass

class Head( protocol.Protocol ):

  def dataReceived( self, data ):
    print "RX'd command: ", data

def main():
  head_Factory = protocol.ServerFactory()
  head_factory.protocol = Head
  reactor.listenTCP( 8000, head_factory )
  
  reactor.run()

if __name__ == "__main__":
  main()
