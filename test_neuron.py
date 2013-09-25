from neuron import *

# Pointless test to check nose functionality
def test_should_create_neuron_instance():
  neuron = Neuron()
  assert( isinstance( neuron, Neuron ) )
