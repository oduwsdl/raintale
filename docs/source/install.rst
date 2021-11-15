============
Installation
============

Raintale is written in Python, but we have created several different ways to install it on Linux/Unix. Raintale is a client of MementoEmbed, so you need to install `MementoEmbed <https://github.com/oduwsdl/MementoEmbed>`_ before starting. Install MementoEmbed first and then follow the directions for your applicable Linux/Unix system below.

Installing on a CentOS 8 System
-------------------------------

If you would like to use the RPM installer for RHEL 8 and CentOS 8 systems:

1. `download the RPM <https://github.com/oduwsdl/raintale/releases>`_ and save it to the Linux server (e.g., ``raintale-0.20211106041644-1.el8.x86_64.rpm``)
2. type ``dnf install raintale-0.20211106041644-1.el8.x86_64.rpm``
3. type ``systemctl start raintale-django.service``

Raintale can now be accessed from ``http://localhost:8100``.

If the service does not work at first, you may need to run ``systemctl start mementoembed.service``.

To remove Raintale, type ``dnf remove raintale`` (it is case sensitive). Removing Raintale stops the associated raintale service and its celery companion. Be patient, sometimes celery takes a long time to stop.

During removal, the directory ``/opt/raintale/raintale_with_wooey/raintale_with_wooey/user_uploads`` is saved to ``/opt/raintale/user_uploads-backup-[DATE].tar.gz`` where [DATE] was the date and time of removal. This is where all story outputs are stored. The administrator may wish to delete or backup this file for future use.

Installing on an Ubuntu 21.04+ System
-------------------------------------

If you would like to use the deb installer for RHEL 8 and CentOS 8 systems:

1. `download the DEB <https://github.com/oduwsdl/MementoEmbed/releases>`_ and save it to the Linux server (e.g., ``raintale-0.20211113202900.deb``)
2. type ``apt-get update`` ⬅️ this may not be necessary, but is needed in some cases to make sure dependencies are loaded
3. type ``apt-get install ./raintale-0.20211113202900.deb`` ⬅️ the ``./`` is important, do not leave it off
4. type ``systemctl start raintale-django.service``

Raintale can now be accessed from ``http://localhost:8100``.

If the service does not work at first, you may need to run ``systemctl start mementoembed``.

To remove Raintale, type ``apt-get remove raintale`` (it is case sensitive). Removing Raintale stops the associated raintale service and its celery companion. Be patient, sometimes celery takes a long time to stop.

During removal, the directory ``/opt/raintale/raintale_with_wooey/raintale_with_wooey/user_uploads`` is saved to ``/opt/raintale/user_uploads-backup-[DATE].tar.gz`` where [DATE] was the date and time of removal. This is where all story outputs are stored. The administrator may wish to delete or backup this file for future use.

Installing on a generic Unix System
-----------------------------------

If you would like to use the generic installer for Unix (including macOS):

1. `download the generic installer <https://github.com/oduwsdl/MementoEmbed/releases>`_ (e.g., ``install-raintale.sh``)
2. type ``sudo ./install-raintale.sh``
3. start Raintale using either ``systemctl start raintale-django.service`` (if your Unix/Linux supports systemd) or ``/opt/raintale/raintale-gui/start-raintale-wui.sh`` if not

Raintale can now be accessed from ``http://localhost:8100``.

To stop Raintale, type ``/opt/raintale/stop-raintale-wui.sh``.

Installing Raintale in a Python Environment
-------------------------------------------

Raintale uses ``pip`` for build and installation. Clone this repository and type the following from the root of the source code:

1. Clone this repository.
2. Change into the directory where it was cloned.
3. `Create a virtualenv <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`_ to separate Raintale's install from other Python installations.
4. Type ```pip install .``` 

Installing the Raintale Web User Interface (WUI) in a Python Environment
------------------------------------------------------------------------

To install the Raintale WUI, do the following:
1. Follow the above instructions for installing Raintale in a Python Environment.
2. Type ``raintale-gui/install-gui.sh``

This installation script will install `Wooey <https://github.com/wooey/Wooey>`_ and other dependencies required to run the Raintale WUI.

Once the installation is complete, to start the Raintale GUI, do the following:
1. Run `raintale-gui/start-gui.sh`.
2. Once the service is started, you can access the Raintale GUI at http://127.0.0.1:8000/. 

To stop the Raintale WUI, type `raintale-gui/stop-gui.sh`.

Improving the performance of the Raintale WUI
---------------------------------------------

Once installed, Raintale's WUI performance can be improved in a few ways.

Configuring Raintale WUI for Postgres
`````````````````````````````````````

By default, the Raintale WUI uses SQLite, which does not perform well for multiple users logging into the same Raintale WUI system. For optimial user experience, the Raintale WUI can be connected to a Postgres database.

1. Install Postgres on a system accessible to the server that on which the Raintale WUI is running. Record that system's host and the port Postgres is running on -- the default port is 5432.
2. Log into Postgres and create a database with postgres for Raintale.
3. Create a user and password.
4. Grant all privileges on the database from step 2 in step 3.
5. Run `/opt/raintale/raintale-gui/set-raintale-database.sh --dbuser [DBUSER] --dbname [DBNAME] --dbhost [DBHOST] --dbport [DBPORT]` -- with DBUSER created from step 3, DBNAME replaced by the database you created in step 2, DBHOST and DBPORT recorded from step 1. The script will prompt you for the password.
6. Restart Raintale as appropriate for your system.

Configuring the Raintale WUI for RabbitMQ
``````````````````````````````````````````````

For optimal process control, the Raintale WUI can use a queueing service like RabbitMQ.

1. Install RabbitMQ on a system accessible to the server that the Raintale WUI is running on. Record that system's hostname and the port that RabbitMQ is running on -- the default port is 5672.
2. Run `/opt/raintale/raintale-gui/set-raintale-queueing-service.sh --amqp-url amqp://[HOST]:[PORT]/` where HOST is the host of the RabbitMQ server and PORT is its port

Enabling Raintale's Experimental Video Stories for the Raintale WUI on CentOS 8
```````````````````````````````````````````````````````````````````````````````

By default, Raintale's video stories are not enabled in the Raintale WUI in CentOS 8 installs. Generating these stories requires `ffmpeg <https://www.ffmpeg.org>`_. Installing ffmpeg on Ubuntu is easy. Installing ffmpeg on CentOS 8 requires using YUM/DNF repositories outside of those provided by CentOS, as detailed in `these instructions <https://linuxize.com/post/how-to-install-ffmpeg-on-centos-8/>`_. Rather than force all CentOS 8 Raintale administrators to go through this process, we have disabled video stories through the Raintale WUI.

To enable them:
1. install ffmpeg
2. Open `/opt/raintale/raintale-gui/add-raintale-scripts.sh` in an editor and remove the # and space from the line containing `Create Video Story.py` so it looks like this (spaces are significant):
```
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/Create Video Story.py"
```
3. Run `/opt/raintale/raintale-gui/add-raintale-scripts.sh`
