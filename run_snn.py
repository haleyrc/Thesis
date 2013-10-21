from datetime import datetime as dt
from pylab import *
from snn import *

if __name__ == "__main__":

  # neuron    = nest.Create( 'iaf_neuron' )
  neuron = IAFNeuron( threshold_voltage = -55. )
  neuron.to_file = True
  neuron.to_screen = True
  neuron.filename = "iafneuron0_" + dt.now().strftime( "%Y%m%d%H%M%S" )

  """
  sine      = nest.Create( 'ac_generator', 1,
                         { 'amplitude': 100.0,
                           'frequency': 2.0 })
  """
  ac_gen = ACGenerator( amplitude = 500., frequency = 2. )

  """
  noise     = nest.Create( 'poisson_generator', 2,
                        [{ 'rate': 70000.0 },
                         { 'rate': 20000.0 }])
  """
  poisson_1 = PoissonGenerator( 70. )
  poisson_2 = PoissonGenerator( 20. )

  # voltmeter = nest.Create( 'voltmeter', 1,
                           # { 'withgid': True })
  # voltmeter = Voltmeter()
  # voltmeter.to_file = True
  # voltmeter.to_screen = True

  # spike = nest.Create( 'spike_detector', 1,
                      # [ { 'label': 'neuron_1-ex' } ] )
  spike = SpikeDetector()

  # nest.SetStatus( spike, { 'to_file': True } )

  # nest.Connect( sine, neuron )
  ac_gen.connect( neuron )

  # nest.Connect( voltmeter, neuron )
  # voltmeter.connect( neuron )

  # nest.Connect( neuron, spike )
  neuron.connect( spike )

  # nest.ConvergentConnect( noise, neuron, [ 1.0, -1.0 ], 1.0 )
  # poisson_1.connect( neuron )
  # poisson_2.connect( neuron )
  convergentConnect( [poisson_1, poisson_2], neuron, [1.2, -1.0] )

  el = EntityList()
  el.add( [ac_gen, poisson_1, poisson_2, neuron, spike] )
  print el

  # nest.Simulate( 1000.0 )
  el.simulate( 1000 )

  print spike.log()
  spike_filename = "spikelog_" + dt.now().strftime( "%Y%m%d%H%M%S" ) + ".csv"
  with open( spike_filename, 'w' ) as f:
    f.write( spike.log() )

  # nest.voltage_trace.from_device( voltmeter )
  # nest.raster_plot.from_device( spike, hist = True )
  # pylab.show()
  gids, times = spike.data()
  subplot( 2, 1, 1 )
  plot( neuron.voltage_trace[0], neuron.voltage_trace[1] )
  xlabel( 'time (ms)' )
  ylabel( 'potential (mV)' )
  title( 'Voltage trace of neuron with id: %s' % neuron.node_id )

  subplot( 2, 1, 2 )
  plot( gids, times, 'b.' )
  axis( [0, 1000, -1, 1] )
  xlabel( 'time (ms)' )
  ylabel( 'gid' )
  title( 'Spike times by neuron id' )
  tight_layout()

  savefig( 'trace%s_%s.pdf' % ( neuron.node_id, dt.now().strftime( "%Y%m%d%H%M%S" ) ) )
  show()
