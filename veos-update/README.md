This script will update a vEOS virtual machine to a different vEOS image.

It leverages a few different modules, so please make sure they are installed prior to running - you
can use ``sudo pip install -r requirements.txt`` to do that.

It also requires a user with privilege 15 access and https transport, and does not support an enable
password at this time.

Example:
   `` ./veos-update.py -u admin -i 192.168.56.10 -s vEOS-lab-4.15.6M.swi``

Todo:

* Release notes?
