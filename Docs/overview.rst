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
of AJAX may by required for seamless user experience).

The server part of web service will communicate with an AppGateway over https
using REST :doc:`webapi`. It is viewed as the Client for the backend
infrastructure, users web browser should not interact directly with the
backend. The AppGateway is very lightweight and its purpose is to pass job
requests to AppServer as well as to answer status requests from Clients (It is
possible that the AppGateway could be extended to accommodate for instance user
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

.. _api_overview:

API overview
------------

The Gateway API allows for:

* Job submission

  + Predefined set of variables can be used to alter the job execution. Four
    types of variables are available:

    - "int" - an integer number with predefined validity range
    - "float" - a floating point number with predefined validity range
    - "string" - a string with predefined dictionary of allowed values
    - "datetime" - a datetime strings with predefined strptime format
    - "int_array" - a list of integer numbers that have common validity range
    - "float_array" - a list of floating point numbers that have a common
      validity range
    - "string_array" - a list of chracter strings that have a common dictionary
      of allowed values
    - "datetime_array" - a list of datetime strings with common predefined
      strptime format
    - "object" - a structure used to combine a set of basic variables
    - "object_array" - a list of objects
    - "set" - name of predefined set of variable values, allows to set several
      variables using one parameter. Also the only way for a job to influence
      internal variables like "PBS queue" or "number of PBS worker nodes".
      Variable of type "set" can only accept values 1 (int) or "1" (string"

  + Each variable has predefined default value therefore jobs do not have to
    specify values for all available variables

* Status query

  + Job status ("Queued", "Running", "Done", ...) can be queried for each job

* Retrieval of job output

  + Job output is stored on a dedicated http server. The URL where output files
    for a job are accessible is available through REST API call.

* Job termination / removal of completed jobs

Service definition
------------------

Each service besides the web interface will consist of two additional
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
    which a job is removed. If set to 0 the jobs are retained indefinitely
    until service quota is exceeded.
    (default: 24 h)
  + max_runtime - Time period in hours (fraction of hour is supported) a job
    can spend in running state. When exceeded the job is killed and removed.
    (default: 12h)
  + max_jobs - Maximum number of jobs running in parallel. (default: 50)
  + scheduler - Select a scheduler to use: pbs, ssh. (default: pbs)
  + username - Select a user to use for the selected scheduler if relevant.
  + queue - Select a queue for the scheduler: pbs - queue name, ssh - hostname. (default: a12h)

* variables - defines allowed input variables for the service. Dictionary keys
  specify variable names. Allowed variable names consist of any combination of
  small and large letters, numbers and an underscore. National characters are
  not allowed [TBC]. Each variable is defined as dictionary with three required
  keys.

  + type - defines type of variable, one of ("int", "float", "string",
    "datetime", "object", "int_array", "float_array", "string_array",
    "datetime_array", "object_array")
  + default - default value
  + values - array with allowed values.

    - For int and float exactly two elements are required: min and max.
    - For string the array defines a list of allowed values. Allowed strings
      can contain national characters [NOT IMPLEMENTED YET].
    - For datetime it should be a string defining the format in which the date
      will be provided. The format should be parsable by strptime python
      function.
    - For object it is a dictionary of components. Each component has the same
      structure as basic variables: string key defining the name and a
      dictionary value with structure described in this section. Nesting of
      objects is allowed however the nesting level is limited via config
      setting. The default nesting level is 0 - no nesting.

  + length - for the "\*_array" variable types defines maximum allowed length
    of user provided list.

* sets - predefined sets of variable values. Each set is a dictionary of
  "variable name":"value" pairs. Values have to be valid according to variable
  definition in "variables" dictionary. Variables not defined in a set will use
  default values unless provided explicitly. Values for variables defined in a
  set can be overridden by specifying them explicitly in the input data. Sets
  allow to override settings for certain reserved variables e.g.: CIS_QUEUE,
  CIS_SCHEDULER

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
                "values" : [0, 10000]
            },
            "B" : {
                "type" : "float",
                "default" : 20.99,
                "values" : [-100, 100]
            },
            "C" : {
                "type" : "string",
                "default" : "alpha",
                "values" : ["alpha", "beta", "gamma", "delta"]
            },
            "D" : {
                "type" : "datetime",
                "default" : "20150120 130000",
                "values" : "%Y%m%d %H%M%S"
            },
            "E" : {
                "type" : "object",
                "default" : {
                    "decay" : 100,
                    "wetscava" : 0.00001
                },
                "values" : {
                    "decay":{
                        "type":"int",
                        "default": 10,
                        "values" : [0,1000000000]
                    },
                    "wetscava":{
                        "type":"float",
                        "default": -9.9E-9,
                        "values" : [-9.9E-9,1E-04]
                    }
                }
            },
            "aA" : {
                "type" : "int_array",
                "default" : [100, 10, 20, 30],
                "values" : [0, 10000],
                "length" : 100
            },
            "aB" : {
                "type" : "float_array",
                "default" : [20.99, 11.11, 0.5, 6.3e-2],
                "values" : [-1000, 1000],
                "length" : 100
            },
            "aC" : {
                "type" : "string_array",
                "default" : ["alpha", "alpha", "delta", beta"],
                "values" : ["alpha", "beta", "gamma", "delta"],
                "length" : 100
            },
            "aD" : {
                "type" : "datetime_array",
                "default" : ["20150120 130000", "20150121 130000"],
                "values" : "%Y%m%d %H%M%S",
                "length" : 5
            },
            "aE" : {
                "type" : "object_array",
                "default" : [],
                "values" : {
                    "aaa":{
                        "type":"string_array",
                        "default": ["test1", "test2"],
                        "values" : ["test1", "test2", "test3", "test4"],
                        "length" : 10
                    },
                    "bbb":{
                        "type":"datetime",
                        "default" : "20150120 130000",
                        "values" : "%Y%m%d %H%M%S"
                    }
                },
                "length" : 100
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
            },
            "Set4" : {
                "aA" : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            }
        }
    }

Service templates are placed in a subdirectory named exactly as the service.
They should contain at least two files "pbs.sh" and "epilogue.sh". The "pbs.sh"
script after substitutions will be executed on Worker Node. The "epilogue.sh"
script is executed after the job finishes and should create "status.dat" file
in job working directory containing one line with jobs' exit code. Additional
template files can be stored in arbitrary directory structure which will be
replicated at WORKDIR of running job. For the templates the Jinja2 template
engine (http://jinja.pocoo.org) is used with a small modification: variables
are defined as @@{variable_name}. Each file in the template directory will be
parsed by the Jinja2 template engine.

Example Test template pbs.sh script::

    #!/bin/sh

    A=@@{A}
    B=@@{B}
    C=@@{C}
    N=@@{aA|length}

    echo $A $B $C $N

    {% for v in aA %}
    echo "Element: @@{loop.index}"
    echo "Value: @@{"%5s"|format(v)}"
    {% endfor %}

    {% for obj in aE %}
    echo "Date: @@{obj.bbb}"
    {% endfor %}

    /bin/hostname
    sleep 10

Reserved variables
------------------

There is a set of variable names that are reserved for special purpose and
cannot be used directly by the service. First class corresponds to variables
that govern the execution of the jobs. They can be altered by the job using
predefined values specified using "sets".

* CIS_SCHEDULER - Select scheduler to use. Can be used for submission to
  computing resources not managed by the central CIŚ scheduler. Currently only
  "pbs" scheduler is supported (main CIŚ scheduler).
* CIS_QUEUE - Queue used by PBS scheduler (default: test_slc6)
* CIS_SSH_HOST - Host name used by SSH scheduler (default: localhost)

Second class consists of automatic variables:

* CIS_CHAIN* - name of a directory containing the output data files of an input
  job. The "*" corresponds to the position of the job in the chain list (see
  :ref:`job_chain`).

Known Bugs
----------

* No unicode support

TODO
----

List of planned / proposed features:

* Improved reaction time - implement inotify triggers
* Validation of config files structure
* Some additional anti-DoS measures:

  + Limit request / second?
  + Compiled python code?
  + Webserver that does not fork for each request ????

* User support (LDAP and/or OpenID login, per user quota, etc)

Enhancements
------------

User authentication and authorization

* Each user is issued an X.509 certificate. The certificate is used by the
  gateway to authenticate user. The CN of the certificate will be the user
  identifier. In addition all payloads can be encrypted using the private key
  of the user and decrypted on the server. This ensures that even when gateway
  is compromised it cannot send requests on behalf of the users as the request
  have to be crypto signed. This allows for secure message exchange over
  RabbitMQ.
* Each job has an owner and users are only allowed to manage their jobs
* A superuser is possible
* RabbitMQ can be used to signal state changes requested by the
  user and can be used internally to achive an asynchronous operation and
  scalability. The exchanges and queues used internally should be on separate vhost
  from exchanges used to handle the client requests. This ensures that even
  compromised gateway cannot affect internal state of the service.
* The fair share handling is moved entirely to the external scheduler
  (preferably slurm) where each user has its own LDAP account. To start jobs as
  dedicated user a service with a subset of superuser priviledges will listen
  to rabbitmq queue. When a message to start a job arrives it will fork a new
  process (check if such worker exists??) which will drop superuser and su into
  the dedicated user. A service will be running in background ensuring that a
  proper kerberos ticket is available.
