========================
Implementation reference
========================

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

Class reference
---------------

.. toctree::
   :maxdepth: 4

   CISAppGateway
   CISAppServer
