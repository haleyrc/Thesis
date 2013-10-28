from snn import *
import re

# Pointless test to check nose functionality
class TestNeuron( object ):

  def setup( self ):
    self.el = EntityList()
    self.neuron = IAFNeuron( threshold_voltage = 1.9 )
    self.spike  = SpikeDetector()
    self.ac_gen = ACGenerator( frequency = 125 )

    self.neuron.connect( self.spike )
    self.ac_gen.connect( self.neuron )

    self.el.add( [self.neuron, self.spike, self.ac_gen ] )

  def test_should_create_neuron_instance( self ):
    assert( isinstance( self.neuron, IAFNeuron ) )

  def test_neuron_should_have_id( self ):
    assert( self.neuron.node_id is not None )

  def test_neuron_should_increment_id( self ):
    next_neuron = IAFNeuron( threshold_voltage = 1.9 )
    assert( next_neuron.node_id == self.neuron.node_id + 1 )

  def test_neuron_should_add_connection( self ):
    assert( len( self.neuron.targets ) == 1 )
    assert( isinstance( self.neuron.targets[0], SpikeDetector ) )

  def test_neuron_should_propagate_spikes( self ):
    self.neuron._spike()
    assert( len( self.spike.spike_stream ) == 1 )

  def test_neuron_should_accumulate_voltage( self ):
    assert( self.neuron.membrane_potential == 0 )
    self.el.simulate( 2 )
    assert( self.neuron.membrane_potential > 0 )

  def test_should_spike_when_threshold_reached( self ):
    self.ac_gen.set_frequency( 1. )
    self.el.simulate( 500 )
    assert( len( self.spike.spike_stream ) > 0 )

class TestSpike( object ):

  def setup( self ):
    self.neuron = IAFNeuron( threshold_voltage = 1.9 )
    self.spike  = SpikeDetector()

    self.neuron.connect( self.spike )

  def test_spike_detector_stream_should_have_correct_source_id( self ):
    self.neuron._spike()
    assert( self.neuron.node_id == self.spike.spike_stream[0][0] )

  def test_spike_stream_should_have_correct_time( self ):
    for i in range( 3 ):
      self.neuron.tick()
    self.neuron._spike()
    for i in range( 3 ):
      assert( len( self.spike.spike_stream[i] ) == 0 )
    assert( len( self.spike.spike_stream[4] ) == 1 )

class TestClocked( object ):

  def setup( self ):
    self.neuron = IAFNeuron( threshold_voltage = 1.9 )

  def test_should_start_at_time_zero( self ):
    assert( self.neuron.time == 0 )

  def test_tick_should_increment_time( self ):
    self.neuron.tick()
    assert( self.neuron.time == 1 )

class TestEntityList( object ):

  def setup( self ):
    self.entities = EntityList()
    self.neuron = IAFNeuron( threshold_voltage = 1.9 )
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
    self.entities.add( [ self.neuron, self.spike ] )
    self.entities.tick()
    assert( self.neuron.time == 1 )
    assert( self.spike.time  == 1 )

class TestACGenerator( object ):

  tol = 0.01

  def setup( self ):
    # Use 125Hz to make period easier to divide
    self.ac_gen = ACGenerator( frequency = 125 )
    self.neuron = IAFNeuron( threshold_voltage = 1.9 )
    self.ac_gen.connect( self.neuron )

  def test_should_have_frequency_and_amplitude( self ):
    assert( self.ac_gen.frequency is not None )
    assert( self.ac_gen.amplitude is not None )

  def test_should_calculate_cycle_time_correctly( self ):
    assert( self.ac_gen.cycle_time == 8 )

  def test_voltage_at_zero_should_be_zero( self ):
    assert( abs( self.ac_gen.voltage ) < self.tol )

  def test_voltage_at_half_period_should_be_zero( self ):
    ticks = self.ac_gen.cycle_time / 2
    for tick in range( int( ticks ) ):
      self.ac_gen.tick()
    assert( abs( self.ac_gen.voltage ) < self.tol )

  def test_voltage_at_period_should_be_zero( self ):
    ticks = self.ac_gen.cycle_time
    for tick in range( int( ticks ) ):
      self.ac_gen.tick()
    assert( abs( self.ac_gen.voltage ) < self.tol )

  def test_voltage_at_quarter_period_should_equal_amplitude( self ):
    ticks = self.ac_gen.cycle_time / 4
    for tick in range( int( ticks ) ):
      self.ac_gen.tick()
    assert( abs( self.ac_gen.voltage - self.ac_gen.amplitude ) < self.tol )

  def test_should_output_voltage_to_target( self ):
    self.ac_gen.tick()
    assert( len( self.neuron.input_queue ) == 1 )

class TestPoissonGenerator( object ):

  tol = 0.05

  def setup( self ):
    self.neuron = IAFNeuron( threshold_voltage = 70. )
    self.poisson = PoissonGenerator( 20000 )
    self.poisson.connect( self.neuron )

  def test_should_have_rate_inverse_of_arg( self ):
    assert( self.poisson.rate == ( 1. / 20000. ) )

  def test_average_should_be_close_to_rate( self ):
    avg = sum( [self.poisson.generate() for i in range(1000000)] ) / 1000000.
    absolute_error = abs( 1 - ( avg / 20000. ) )
    assert( absolute_error < self.tol )

  def test_should_output_noise_to_target( self ):
    self.poisson.tick()
    assert( len( self.neuron.input_queue ) == 1 )

class TestVoltmeter( object ):

  def setup( self ):
    self.voltmeter = Voltmeter()

  def test_voltmeter_should_have_a_default_filename( self ):
    assert( self.voltmeter.filename == "voltage" )

  def test_voltmeter_should_have_a_meaningful_filename( self ):
    neuron = IAFNeuron( 2. )
    self.voltmeter.connect( neuron )
    pattern = re.compile( "iafneuron_\d+" )
    assert( pattern.match( self.voltmeter.filename ) != None )
