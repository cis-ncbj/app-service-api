========
Overview
========

Goals
-----

The WebServices backend infrastructure was designed with following goals in
mind:

* Minimize possibility of successful attack on CIŚ computing
  infrastructure via web services

  + Separate the web interface from computing resources
  + Validate input sent by the user

* Prepare common simple API for web service designers
* Remain agnostic with regards to choice of programming language by web
  service designers

Design
------

The design of web service frontend remains at discretion of its developer.
However it will usually consist of HTML web pages displayed by users web
browser that communicate with web service dedicated web server (some usage
of AJAX may by required for seamles user experience).

The server part of web service will communicate with an AppGateway over https
using REST :doc:`webapi`. It is viewed as the Client for the backend
infrastructure, users web browser should not interact directly with the
backend. The AppGateway is very lightweight and its purpose is to pass job
requests to AppServer as well as to answer status requests from Clients (It is
possible that the AppGateway could be extended to accomodate for instance user
authentication). The AppGateway will be positioned inside the DMZ, however it
should not be accessible from outside networks - the assumption is that Clients
will also reside inside DMZ. The AppServer is placed inside the internal CIŚ
network and can access computational resources in particular file servers and
PBS scheduler. AppGateway will communicate with AppServer using shared file
system - each new request is represented as a new file that AppServer will
process. The job status is represented by symbolic links at appropriate paths.

Communication between system components::

    Web Browser  (WAN)
        ⇵ HTTPS
    Client       (DMZ)
        ⇵ HTTPS
    AppGateway   (DMZ)
        ⇵ NFS
    AppServer    (LAN)
        ⇵ PBS / SSH
    Worker Nodes (LAN)

API overview
------------

The Gateway API allows for:

* Job submission

  + Predefined set of variables can be used to alter the job execution. Four
    types of variables are available:

    - "int" - an integer number with predefined validity range
    - "float" - a floating point number with predefined validity range
    - "string" - a string with predefined dictionary of allowed values
    - "set" - name of predefined set of variable values, allows to set several
      variables using one parameter. Also the only way for a job to influence
      internal variables like "PBS queue" or "number of PBS worker nodes".
      Varliable of type "set" can only accept values 1 (int) or "1" (string"

  + Each variable has predefined default value therefore jobs do not have to
    specify values for all available variables

* Status query

  + Job status ("queued", "running", "done", ...) can be queried for each job

* Retrival of job output

  + Job output is stored on a dedicated http server. The URL where output files
    for a job are accessible is available through REST API call.

* Job termination / removal of completed jobs

Service definition
------------------

Each service besides the web interface will consist of two addictional
components.

* Service configuration - a file that defines allowed variables and their
  values.
* Script and input data templates - templates for scripts that will be executed
  on Worker Nodes and templates for input data files. The templates contain
  keywords that will be substituted with actual values as requested by the
  client.

The service configuration is stored in JSON format in a file named exactly as
the service. File consists of three dictionaries:

* config - defines key:value pairs that modify service behaviour.

  + quota - Maximum disk size utilisation by service output files in MB. When
    quota is exceeded oldest results will be removed automatically.
    (default: 10000 MB)
  + job_size - Maximum size (in MB) of output for one job. This value is used
    by the scheduler to predict required disk space when starting new jobs.
    (default: 50 MB)
  + min_lifetime - Time period in hours (fraction of hour is supported) when
    job cannot be automatically removed when service quota is exceeded.
    (default: 2 h)
  + max_lifetime - Time period in hours (fraction of hour is supported) after
    which a job is removed. If set to 0 the jobs are retained indefinately
    until service quota is exceeded.
    (default: 24 h)
  + max_jobs - Maximum number of jobs running in parallel. (default: 50)

* variables - defines allowed input variables for the service. Dcitionary keys
  specify variable names. Allowed variable names consist of any combination of
  small and large letters, numbers and an underscore. National characters are
  not allowed [TBC]. Each variable is defined as dictionary with three required
  keys.

  + type - defines type of variable, one of ("int", "float", "string")
  + default - default value
  + values - array with allowed values. For int and float exactly two elemets
    are required: min and max. For string array defines a list of allowed
    values. Allowed strings can contain national characters [NOT IMPLEMENTED YET].

* sets - predefined sets of variable values. Each set is a dictionary of
  "variable name":"value" pairs. Values have to be valid according to variable
  definition in "variables" dictionary. Variables not defined in a set will use
  default values unless provided explicitely. Values for variables defined in a
  set can be overriden by specifying them explicitely in the input data.

Keep in mind that JSON unlike Python does not allow dangling ',' separators.

Example Test service configuration::

    {
        "config" : {
            "quota" : "10000"
        },
        "variables" : {
            "A" : {
                "type" : "int",
                "default" : 100,
                "values" : [0,10000]
            },
            "B" : {
                "type" : "float",
                "default" : 20.99,
                "values" : [-100,100]
            },
            "C" : {
                "type" : "string",
                "default" : "alpha",
                "values" : ["alpha", "beta", "gamma", "delta"]
            }
        },
        "sets" : {
            "Set1" : {
                "A" : 1,
                "B" : -55.55,
                "C" : "delta"
            }
            "Set2" : {
                "A" : 1000,
                "C" : "gamma"
            },
            "Set3" : {
                "C" : "beta"
            }
        }
    }

Service templates are placed in a subdirectory named exactly as the service.
They should contain at least two files "pbs.sh" and "epilogue.sh". The "pbs.sh"
script after substitutions will be executed on Worker Node. The "epilogue.sh"
script is executed after the job finishes and should create "status.dat" file
in job working directory containing one line with jobs' exit code. Additional
template files can be stored in arbitraty directory structure which will be
replicated at WORKDIR of running job. Each file will be parsed and all
occurances of @@{variable_name} will be replaced with value specified for
variable "variable_name".

Example Test template pbs.sh script::

    #!/bin/sh

    A=@@{A}
    B=@@{B}
    C=@@{C}

    echo $A $B $C
    /bin/hostname
    sleep 10


Known Bugs
----------

* No unicode support
* Lack of proper handling for all PBS job states e.g. "C"

TODO
----

List of planned / proposed features:

* Resource quota system:

  + Per service job life-time setting
  + Per service disk quota
  + Per service concurent jobs quota
  + Garbage collector

* Improved reaction time - implement inotify triggers
* Validation of config files structure
* Some additional anti DOS measures:

  + Limit request / second?
  + Compiled python code?
  + Webserver that does not fork for each request ????

* User support (LDAP and/or OpenID login, per user quota, etc)
