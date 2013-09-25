from Queue import PriorityQueue

class Clocked( object ):

  def __init__( self ):
    self.time = 0

  def tick( self ):
    self.time += 1

class IAFNeuron( Clocked ):

  next_id = 0

  def __init__( self ):
    super( IAFNeuron, self ).__init__()
    self.targets = []
    self.node_id = IAFNeuron.next_id
    IAFNeuron.next_id += 1

  def __repr__( self ):
    return str( self.__class__ )

  def connect( self, dest ):
    self.targets.append( dest )

  def spike( self ):
    for target in self.targets:
      target.spike( self.node_id )

class ACGenerator( object ):

  def __init__( self ):
    pass

  def __repr__( self ):
    pass

class PoissonGenerator( object ):

  def __init__( self ):
    pass

  def __repr__( self ):
    pass

class Voltmeter( object ):

  def __init__( self ):
    pass

  def __repr__( self ):
    pass

class SpikeDetector( Clocked ):

  def __init__( self ):
    self.spike_stream = PriorityQueue()
    super( SpikeDetector, self ).__init__()

  def __repr__( self ):
    return str( self.__class__ )

  def spike( self, source_id ):
    # First parameter is place holder for tick time
    self.spike_stream.put( (0, source_id ) )

  def tick( self ):
    self.time += 1

class EntityList( object ):

  def __init__( self ):
    self.entity_list = []

  def __len__( self ):
    return len( self.entity_list )

  def add( self, args ):
    if not isinstance( args, list ):
      args = [args]
    
    for arg in args:
      self.entity_list.append( arg )

  def tick( self ):
    for entity in self.entity_list:
      entity.tick()
