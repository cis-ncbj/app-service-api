========================
Implementation reference
========================

.. _source-code:

Source Code
-----------

The source code is available through git repository::

    git clone ssh://<user_name>@usrint.cis.gov.pl/mnt/home/kklimaszewski/GitRepos/WebServices
    cd WebServices
    git submodule init
    git submodule update

The repository contains code for AppGateway, AppServer and example service
MultiNest as well as this documentation.

Updating the code to the latest version::

    git pull
    git submodule update

Running Webservice locally
--------------------------

Setup
+++++

First checkout the source code (see :ref:`source-code`).

Then we create a working directory::

    mkdir WebServicesRun
    cd WebServicesRun
    cp -r ../WebServices/AppServer/Services .
    cp ../WebServices/AppServer/CISAppServer.json .
    cp ../WebServices/AppGateway/CISAppGateway.json .

To test new service put it's configuration files into WebServicesRun/Services.
Edit the CISAppGateway.json configuration file and add the new service to
"allowed_services" list.

To change where the logs of AppGateway and AppServer are stored edit the
CISAppGateway.json and CISAppServer.json configuration files.

Start
+++++

Now we can start the AppServer and the AppGateway::

    cd WebServicesRun
    ../WebServices/AppServer/cisapps start
    ../WebServices/AppGateway/cisappg

The AppServer will run in background. To see what is going check the log file::

    tail -f /tmp/CISAppServer.log

Tests
+++++

For job submission we can use curl. The AppGateway listens on port 5000 by
default::

    curl -i -H "Content-Type: application/json" -X POST \
        -d '{"service":"Test","api":1.0, "input":{"2Float":10.0}}' \
        http://localhost:5000/submit

As a result we will obtain a JOBID. To check the job status::

    curl -i http://localhost:5000/status/<JOBID>

More API calls are described in :doc:`webapi`.

Stop
++++

The AppGateway is stopped by sending the interrupt signal ([ctrl] + C).
The AppServer is stopped with stop command::

    cd WebServicesRun
    ../WebServices/AppServer/cisapps stop

Information about other commands and options can be displayed::

    ../WebServices/AppServer/cisapps --help

Class reference
---------------

.. toctree::
   :maxdepth: 4

   CISAppGateway
   CISAppServer
