from snn import *

# Pointless test to check nose functionality
def test_should_create_neuron_instance():
  neuron = IAFNeuron()
  assert( isinstance( neuron, IAFNeuron ) )
