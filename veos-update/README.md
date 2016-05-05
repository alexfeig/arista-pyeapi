This script will take an IP address and username as arguments and use SCP to copy a vEOS .swi image to a veos virtual machine. It will then set the boot image to the new .swi and reload it.

Prior to updating, it will write the configuration.

Todo:

* Downgrade handling?
* Release notes?
* Diff config before saving?