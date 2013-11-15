# Thesis

Work done toward the completion of my Master's thesis at the Rochester Institute of Technology.

## Change Log:

### Release 1.0:

A spiking neural network can be created which consists of basic integrate-and-fire neurons. These neurons show both absolute and relative refractory periods as well as basic spike-rate adaptation.

Both alternating current and Poisson noise generators are provided for testing neuronal dynamics.

Sample usage driver programs are given which create some trivial networks and graph the neuron potential and spike events generated.

A test file is provided which ensures proper behavior as features are added.

#### TODO:

[ ] The logging system is very inefficient and needs to be replaced. This will happen in a future release which integrates with a database for central logging of node events.
[ ] The graphing functionality is barebones and produces sub-optimal visualizations of events. The EEG graph specifically is difficult to
interpret and requires some clean-up to be maximally effective.
[ ] Producing a series of jpeg frames which can then be converted into a video would serve as a very good visualization, but this is a low-priority feature as this time.

### Release 2.0 (In Progress)

  The existing spiking neural network infrastructure is modified to include the
  necessary networking components which will allow nodes (software) to be
  instantiated on a distributed system of units (hardware) with a central head
  node that maintains a mapping of node GIDs to unit IP address.

  The current implementation will rely on this central node, but ideally the
  network would be fully decentralized with a phone-tree style data propagation
  system for address maps and GID reservation.

  A sample (non-final) network flow is provided below for reference.

  > #### Initialization
  > 1. The head unit is started
  > 1. The head unit is initialized
  > 1. A new unit is started
  > 1. The unit tells the head unit its ip address
  > 1. The unit asks the head unit what the next available gid is
  > 1. The unit tells the head unit to reserve n gid's where n is the number of local nodes to be initalized on the unit
  > 1. The head unit maps the requested gid's to the unit's ip address
  > 1. The unit creates its local nodes with the requested gid's

  > #### Mapping
  > 1. The head unit sends a gid map to each connected unit where a unit's unique gids are attached to its ip address

  > #### Running
  > 1. The head unit sends a tick command to all connected units
  > 1. Each unit ticks its internal nodes
  > 1. For each node with an outbound (non-locally destined) output:
  >   1. Connect to the node designated in the external address map
  >   1. Send the output with the appropriate gid included

## Upcoming changes:
[ ] Modification of the node types to incorporate message passing via sockets.  This will allow nodes to be distributed across machines as well as across processes on the same machine. This is the focus of the next major release.
[ ] Integration of a database logging system for node information (membrane potential, spike events, etc.). This will allow centralized analysis of nodes across machines and processes.
[ ] Addition of a lightweight web-based interface for instantiating and monitoring nodes across the network.

