from random import expovariate as expo
from collections import defaultdict
from math import sin, pi, exp

class NodeType( object ):

  def __repr__( self ):
    return "<" + self.__class__.__name__ + ", id:" + str( self.node_id ) + ">"

class IAFNeuron( NodeType ):
  '''A basic integrate-and-fire neuron.

     Attributes:
       time                  : The internal time of the neuron
       weights               : An array of weights representing the strength of
                               the connection between this neuron and its targets
       node_id               : A unique identifier for distinguishing multiple 
                               neurons
       input_queue           : A dictionary of inputs to the neuron keyed by time
                               and containing input voltages
       resting_potential     : The absolute potential of the neuron with no
                               inputs
       reset_potential       : The relative potential of a neuron with no inputs
                               or which is currently refractory
       threshold_voltage     : The voltage past which the neuron should emit a
                               spike event
       refractory_period     : The length of time for which the neuron should be
                               refractory following a spike event (in ms)
       spike_time            : The timestamp of the latest spike event for this
                               neuron
       membrane_time_constant: A constant which represents the ratio of the cell
                               membrane's resistance to its capacitance
       membrane_capacitance  : The capacitance of the cell membrane (in pF)
       membrane_resistance   : The resistance of the cell membrane (in Ohms)
       propagation_delay     : The delay between the emission of a spike event
                               and the spike occurring at the target node
       voltage_trace         : A list of lists where the first element is a list
                               of times, and the second is a list of voltage
                               values corresponding to those times
  '''

  next_id = 0

  def __init__( self, threshold_voltage, to_file = False, to_screen = False ):
    self.to_file = to_file
    self.to_screen = to_screen
    self.voltage_trace = [[],[]]
    self.time = 0
    self.targets = []
    self.weights = defaultdict( lambda: 1. )
    self.node_id = IAFNeuron.next_id
    IAFNeuron.next_id += 1
    self.input_queue = defaultdict( list )
    self.resting_potential = -70
    self.reset_potential = -70 - self.resting_potential
    self.threshold_voltage = threshold_voltage - self.resting_potential
    self.refractory_period = 2
    self.spike_time = None
    self.membrane_time_constant = 20.
    self.membrane_capacitance = 250
    self.membrane_resistance = \
        self.membrane_time_constant / self.membrane_capacitance
    self.propagation_delay = 1
    self.reset()

  def _calculate_potential( self ):
    '''Recalculates the membrane potential for each time slice based on the
       standard integrate-and-fire dynamics equation.
    '''

    if self.spike_time:
      rel_refractoriness_amplitude = exp( -1 / ( self.time - self.spike_time ) )
    else:
      rel_refractoriness_amplitude = 1.

    # Is this a mistake? Fix this once graphing is set up.
    rel_refractoriness_amplitude = 1.

    input_current = sum( self.input_queue[self.time] ) * self.membrane_resistance
    self.membrane_potential = \
        self.membrane_potential + \
        rel_refractoriness_amplitude * \
        ( -self.membrane_potential + input_current ) / \
        self.membrane_time_constant

  def connect( self, dest, weight = 1. ):
    '''Connects the output of this neuron to the specified target with a weight
       specified by the user. Weights are positive for excitatory neurons and 
       negative for inhibitory neurons.
    '''

    self.targets.append( dest )
    self.weights[ dest.node_id ] = weight

  def input( self, input_data ):
    '''Used by a calling source to append spike data to the time slice specified
       in the input data tuple.

       The input data tuple should be in the form: (input time, input voltage)
    '''

    time, voltage = input_data
    self.input_queue[time].append( voltage )

  def _log( self ):
    '''Log the current state of the neuron either to file, to screen, or both
       based on the state of the relevant member parameters (to_file, to_screen)
       in the format (id,time,membrane potential).

       TODO: This function needs to be changed to prevent file opening, closing,
             and writing at each time step.
    '''

    output_string = "%s,%s,%s\n" % \
      ( self.node_id, self.time, self.membrane_potential_actual() )

    # Append voltage information to the trace variables for future graphing
    self.voltage_trace[0].append( self.time )
    self.voltage_trace[1].append( self.membrane_potential_actual() )

    if self.to_file:
      with open( self.filename + '.csv', 'a' ) as f:
        f.write( output_string )

    if self.to_screen:
      print output_string,

  def membrane_potential_actual( self ):
    '''Function to return the membrane potential adjusted to be not relative to
       the resting potential.

       Returns:
          The actual membrane potential adjusted relative to the resting
          potential.
    '''

    return self.membrane_potential + self.resting_potential

  def _output( self ):
    '''Helper function to indicate whether the previous time slice included a
       spike event.

       Returns:
         Unity if there was a spike in the last time slice, zero otherwise.
    '''

    if self.spike_time == self.time - 1:
      return 1
    
    return 0

  def refractory( self ):
    '''Returns a boolean value indicating whether the neuron is currently within
       the absolute refractory period

       Returns:
         False: if the neuron is not currently within the absolute refractory
                period following a recent spike.

         True : otherwise.
    '''

    if ( self.spike_time is None ) or \
      ( self.time > ( self.spike_time + self.refractory_period ) ):
      return False

    return True

  def reset( self ):
    '''Resets the neuron's membrane potential to the value specified in the 
       reset_potential variable.

       Note: This is relative to the resting potential.
    '''

    self.membrane_potential = self.reset_potential

  def _spike( self ):
    '''Initiates the transmission of a spike at a time equal to the current time 
       plus the propagation delay. Also sets the most recent spike time to the 
       current spike time for tracking of refractory periods and resets the 
       membrane potential to the resting value.
    '''

    for target in self.targets:
      target.spike( ( self.time + self.propagation_delay, self.node_id, 
                      self.weights[ target.node_id ] ) )

    # Simulate spike-rate adaptation by increasing capacitance after a spike
    # TODO: make the adaptation rate a model parameter
    self.membrane_capacitance = 1.1 * self.membrane_capacitance
    self.membrane_resistance = \
        self.membrane_time_constant / self.membrane_capacitance

    self.spike_time = self.time
    self.reset()

  def spike( self, spike_data ):
    '''A wrapper around the input function which emits a delta shape spike to
       the current neuron's input queue at the specified time. This is provided
       for continuity with other node types.
    '''

    time, _, voltage = spike_data
    self.input( ( time, voltage ) )

  def tick( self ):
    '''Advances the internal time of the neuron and catalyzes the necessary 
       update and logging functions.
    '''

    if self.refractory():
      self.membrane_potential = self.reset_potential
    else:
      self._calculate_potential()

    self._log()

    if self.membrane_potential > self.threshold_voltage:
      self._spike()

    self.time += 1

class ACGenerator( NodeType ):
  '''A node class which injects a sinusoidal current into its target with
     frequency and amplitude specified by the user.

     This class is used primarily for testing the dynamics of the neuron model
     by injecting a known, but varying voltage into the neuron which will
     ideally cause observable spike events.

     Attributes:
       node_id   : An id used to distinguish between multiple ACGenerator 
                   instances
       time      : The internal time of the generator
       frequency : The frequency of the current (in Hz)
       amplitude : The amplitude of the generated sine wave current
       cycle_time: The time (in ms) of a single cycle of the current
       voltage   : The current potential of the generator
       target    : The target of the generator's output
  '''

  next_id = 0

  def __init__( self, frequency = 60, amplitude = 1. ):
    self.node_id = ACGenerator.next_id
    ACGenerator.next_id += 1
    self.time = 0
    self.frequency = frequency
    self.amplitude = amplitude / 2.
    self.cycle_time = 1000. / self.frequency
    self.voltage = 0
    self.target = None

  def _update_voltage( self ):
    '''Calculates a new voltage value governed by the cycle time and amplitude
       of the desired alternating current.
    '''

    self.voltage = sin( 
        ( self.time / self.cycle_time ) * 2 * pi ) * self.amplitude

  def connect( self, dest ):
    '''Connects the output of this generator to the specified target.
    '''

    self.target = dest

  def output( self ):
    '''Generate an input on the target with the latest calculated voltage value.
    '''

    self.target.input( ( self.time, self.voltage ) )

  def set_frequency( self, new_freq ):
    '''Function used to change the frequency of the generator. This function
       also updates the cycle time as it is a calculated attribute.
    '''

    self.frequency = new_freq
    self.cycle_time = 1000. / self.frequency

  def tick( self ):
    '''Updates the generator's internal time, recalculates the output voltage,
       and emits an output to the target using this new value.
    '''
    
    self.time += 1
    self._update_voltage()
    self.output()

class PoissonGenerator( NodeType ):
  '''Generator for a noisy current stream governed by a Poisson process.

     This class invokes the Python standard library to generate a noisy current
     stream. Note that the standard library takes rates which are an inverse of 
     the frequency and the input parameter is thus converted during initialization.

     Attributes:
       node_id: A unique identifier for distinguishing multiple PoissonGenerator
                instances
       rate   : The inverse frequency of the rate provided by the user
       target : The child node which receives the output of the PoissonGenerator
       time   : Used for timestamping outputs in the target's input queue
       weight : The strength of the connection between the PoissonGenerator and 
                its target node
  '''

  next_id = 0

  def __init__( self, rate ):
    '''Note: This function takes a rate expressed in kHz.

    '''

    self.node_id = PoissonGenerator.next_id
    PoissonGenerator.next_id += 1
    self.rate = 1. / rate
    self.target = None
    self.time = 0.
    self.weight = 0.

  def connect( self, dest, weight = 1. ):
    '''Connects the output of this generator to the specified target with a 
       weight specified by the user. Weights are positive for excitatory 
       generators and negative for inhibitory generators.
    '''

    self.target = dest
    self.weight = weight

  def generate( self ):
    '''Utilizes the Python standard library function for sampling from an
       exponential distribution.

       Returns:
         A random value governed by the exponential distribution with the user
         supplied rate.
    '''

    return expo( self.rate )

  def output( self ):
    '''Generate an input on the target with the generated random value scaled by
       the user supplied weight.
    '''

    self.target.input( ( self.time, self.generate() * self.weight ) )
    
  def tick( self ):
    '''This method is provided for compatibility with the EntityList tick method.
    '''

    self.time += 1
    self.output()

'''
class Voltmeter( NodeType ):

  next_id = 1

  def __init__( self ):
    self.node_id = Voltmeter.next_id
    Voltmeter.next_id += 1
    self.filename = "voltage"
    self.to_file = False
    self.to_screen = False
    self.target = None
    self.time = 0

  def _fix_filename( self ):
    self.filename = "_".join( 
      ( self.target.__class__.__name__.lower(), str( self.target.node_id ) ) )

  def connect( self, dest ):
    self.target = dest
    self._fix_filename()

  def output( self ):
    # output_string = "%s\t%s %s\n" % \
    output_string = "%s,%s,%s\n" % \
      ( self.target.node_id, self.time, self.target.membrane_potential_actual() )

    if self.to_file:
      with open( self.filename + '.csv', 'a' ) as f:
        f.write( output_string )

    if self.to_screen:
      print output_string,

  def tick( self ):
    self.output()
    self.time += 1
'''

class SpikeDetector( NodeType ):
  '''Node for logging spike events for later graphing and analysis.

     This class represents a node which can be set as the target for spike events
     from the neuron class. This information can then be used to produce graphs
     based on the spike events for a network, as well as to calculate the spike
     rate.

     Attributes:
       node_id     : A unique identifier for distinguishing multiple SpikeDector
                     instances
       spike_stream: A dictionary of spike events keyed by time and containing
                     the id of the spiking node
       time        : The internal time of the SpikeDetector node
  '''

  next_id = 0

  def __init__( self ):
    self.node_id = SpikeDetector.next_id
    SpikeDetector.next_id += 1
    self.spike_stream = defaultdict( list )
    self.time = 0

  def data( self ):
    '''Returns a tuple of lists where the first list is a sorted collection of
       node ids and the second list are the corresponding spike times for those
       ids. This is used for creating spike time raster plots in the calling
       program.

       Returns:
         A tuple of two lists where the first element contains node ids and the
         second contains spike times corresponding to the matching gid.
    '''

    keys = sorted( self.spike_stream.keys() )
    gids = []
    spike_times = []

    for key in keys:
      for spike in self.spike_stream[key]:
        gids.append( key )
        spike_times.append( spike )

    return ( gids, spike_times )
        

  def log( self ):
    '''Build a string log of the spike events for easy output to screen and file.
    '''

    log = ""
    for time in sorted( self.spike_stream ):
      for node_id in self.spike_stream[time]:
        log += "%s,%s\n" % ( time, node_id )

    return log

  def spike( self, spike_data ):
    '''Append a spike event log entry with the time and node id specified in the
       spike data.
    '''

    time, node_id, _ = spike_data
    self.spike_stream[time].append( node_id )

  def tick( self ):
    '''Advance the internal time of the detector node.'''

    self.time += 1

class EntityList( object ):
  '''A class for collecting nodes in the network for easier updating.

     This class maintains an internal list of nodes which are all updated using
     their respective tick events with a single call to the EntityList tick
     event.

     Attributes:
       entity_list: A list of tracked entities to be updated at each tick event
  '''

  def __init__( self ):
    self.entity_list = []

  def __len__( self ):
    return len( self.entity_list )

  def __repr__( self ):
    return "[" + ", ".join(str( entity ) for entity in self.entity_list) + "]"

  def add( self, args ):
    '''Appends a new entity to the list. This can be either a singular entity
       or a list of entities.
    '''

    if not isinstance( args, list ):
      args = [args]
    
    for arg in args:
      self.entity_list.append( arg )

  def tick( self ):
    '''Call the tick method of all entities, thus updating the time of the entire
       specified network.
    '''

    for entity in self.entity_list:
      entity.tick()

  def simulate( self, simulation_time ):
    '''Run a simulation for a given number of milliseconds by continually calling
       the tick function of each managed entity.
    '''
    for i in range( simulation_time + 1 ):
      self.tick()

def convergentConnect( sources, dest, weights ):
  '''Function for connecting a large number of sources to a single destination
     for faster network construction. The sources and weights should be specified
     as lists and should be of equal size.
  '''

  for source, weight in zip( sources, weights ):
    source.connect( dest, weight )
