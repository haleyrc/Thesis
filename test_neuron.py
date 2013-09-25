from snn import *

# Pointless test to check nose functionality
class TestNeuron( object ):

  def setup( self ):
    self.neuron = IAFNeuron()
    self.spike  = SpikeDetector()

    self.neuron.connect( self.spike )

  def test_should_create_neuron_instance( self ):
    assert( isinstance( self.neuron, IAFNeuron ) )

  def test_neuron_should_have_id( self ):
    assert( self.neuron.node_id is not None )

  def test_neuron_should_increment_id( self ):
    next_neuron = IAFNeuron()
    assert( next_neuron.node_id == self.neuron.node_id + 1 )

  def test_neuron_should_add_connection( self ):
    assert( len( self.neuron.targets ) == 1 )
    assert( isinstance( self.neuron.targets[0], SpikeDetector ) )

  def test_neuron_should_propagate_spikes( self ):
    self.neuron.spike()
    assert( self.spike.spike_stream.qsize() == 1 )

class TestSpike( object ):

  def setup( self ):
    self.neuron = IAFNeuron()
    self.spike  = SpikeDetector()

    self.neuron.connect( self.spike )

  def test_spike_detector_stream_should_have_correct_source_id( self ):
    self.neuron.spike()
    assert( self.neuron.node_id == self.spike.spike_stream.get()[1] )

class TestClocked( object ):

  def setup( self ):
    self.neuron = IAFNeuron()

  def test_should_start_at_time_zero( self ):
    assert( self.neuron.time == 0 )

  def test_tick_should_increment_time( self ):
    self.neuron.tick()
    assert( self.neuron.time == 1 )

class TestEntityList( object ):

  def setup( self ):
    self.entities = EntityList()
    self.neuron   = IAFNeuron()
    self.spike    = SpikeDetector()

    self.neuron.connect( self.spike )

  def test_add_should_take_one_argument( self ):
    self.entities.add( self.neuron )

  def test_add_should_add_an_entity( self ):
    self.entities.add( self.neuron )
    assert( len( self.entities ) == 1 )

  def test_add_should_take_multiple_arguments( self ):
    self.entities.add( [self.neuron, self.spike ] )
    assert( len( self.entities ) == 2 )

  def test_tick_should_update_all_entities( self ):
    self.entities.add( [self.neuron, self.spike ] )
    self.entities.tick()
    assert( self.neuron.time == 1 )
    assert( self.spike.time  == 1 )
