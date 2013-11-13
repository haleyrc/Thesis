from datetime import datetime as dt
from random import randint
from pylab import *
from snn.snn import *

def main():

  network_size = 20

  spike = SpikeDetector()
  neurons = []
  poissons = []
  generators = []

  for i in range( network_size ):
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

  output_neuron = IAFNeuron( threshold_voltage = -55 )
  output_neuron.to_file = False
  output_neuron.to_screen = False
  convergentConnect( neurons, output_neuron, [( val + 1 ) * 30 for val in range( network_size )] )
  output_neuron.connect( spike )

  el = EntityList()
  el.add( generators )
  el.add( poissons )
  el.add( neurons )
  el.add( output_neuron )
  el.add( spike )

  el.simulate( 1000 )


if __name__ == "__main__":

  main()
