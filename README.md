# Requirements

* libvirt installed
* qemu-img available

# Setup

* Setup WAN network that provides internet access to nodes under test
* Setup client VM that will act as a client to the node under test
  * needs to have two interfaces
    * one for talking to the VM from the host
    * one that is dynamically attached to the node under test client network
# gluon-testauto
