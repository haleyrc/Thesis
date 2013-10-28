# Thesis

Work done toward the completion of my Master's thesis at the Rochester Institute of Technology.

## Release Log:

  ### 1.0:

    A spiking neural network can be created which consists of basic
    integrate-and-fire neurons. These neurons show both absolute and relative
    refractory periods as well as basic spike-rate adaptation.

    Both alternating current and Poisson noise generators are provided for
    testing neuronal dynamics.

    Sample usage driver programs are given which create some trivial networks and
    graph the neuron potential and spike events generated.

    A test file is provided which ensures proper behavior as features are added.

    #### TODO:
      * The logging system is very inefficient and needs to be replaced. This
        will happen in a future release which integrates with a database for
        central logging of node events.
      * The graphing functionality is barebones and produces sub-optimal
        visualizations of events. The EEG graph specifically is difficult to
        interpret and requires some clean-up to be maximally effective.
      * Producing a series of jpeg frames which can then be converted into
        a video would serve as a very good visualization, but this is
        a low-priority feature as this time.

## Upcoming changes:
  * Modification of the node types to incorporate message passing via sockets.
    This will allow nodes to be distributed across machines as well as across
    processes on the same machine. This is the focus of the next major release.
  * Integration of a database logging system for node information (membrane
    potential, spike events, etc.). This will allow centralized analysis of
    nodes across machines and processes.
  * Addition of a lightweight web-based interface for instantiating and
    monitoring nodes across the network.
