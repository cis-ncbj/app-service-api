=======
Web API
=======

CIŚ WebService REST API

Job submission
--------------

Jobs are submitted via POST request on http://app-gw.cis.gov.pl/api/submit or
https://app-gw.cis.gov.pl/api/submit. The non encrypted accesss point will be
deprecated for production version of CIŚ WebServices. For testing purposes
developement version of the API is available at:
https://app-gw.cis.gov.pl/api-devel/submit

The POST request should contain job attributes either in JSON format. The data
payload should be a JSON dictionary of key value pairs. The only keys that are
allowed are as follows:

* service - name of the service [required]
* api - API level that the client uderstands [required]. Currently only level
  1.0 is supported.
* input - dictionary of key value pairs corresponding to input variables
  supported by the service (see :ref:`api_overview`)
* chain - list of job IDs to use as an input (see :ref:`job_chain`)
* name - name of the job for easy identification by the user [NOT IMPLEMENTED]

If the input dictionary is not specified the job will use default input values.
All values provided by the client are verified. Example data payload.::

    {
        "service" : "MultiNest",
        "api" : 1.0,
        "input" : {
            "live_points" : 10000,
            "nodes_max" : 100
        },
        "chain" : [
            "PreNestA_30ecad7d-41be-48bc-aaaa-131f894052a8_nlfsvY",
            "PreNestB_50ecad7d-41be-48bc-bbbb-131f894052a8_nlfsvY",
        ]
    }

The request will return an Job ID e.g.:

    MultiNest_40ecad7d-41be-48bc-9d87-131f894052a8_nlfsvY

The Job ID should be stored for duration of a session. It will be used when
performing other API requests. Simple implementation can store it as a cookie
in the users we browser.

Example implementation in python::

    import requests
    import json
    import flask

    def submit(payload):
        """ Submit job request to CIŚ AppGateway

        :param payload: dictionary of name, value pairs that defines job
            parameters
        """
        # Service name
        payload['service'] = "MultiNest"
        # API url
        url = "http://app-gw.cis.gov.pl/api/submit"
        # The data will be sent as JSON payload
        headers = {'content-type': 'application/json'}
        # Send the POST request
        try:
            # For testing set verify=False as we use self signed cert.
            # For production provide CA bundle path as value of the verify
            # attribute
            r = requests.post(url, data=json.dumps(req_data), headers=headers,
                              verify=False)
        except:
            flask.flash(u"Cannot communicate with AppGateway.")
            return flask.redirect('/')

        # Check if server returned Job ID. It will start with the service name
        if r.text.startswith('MultiNest'):
            flask.flash(u"Job submitted successfuly.")
            # Store the Job ID as a cookie
            resp = flask.make_response(flask.redirect('/'))
            resp.set_cookie('CISMultiNestJobID', r.text)
            return resp

        # Error returned
        flask.flash(r.text)
        return flask.redirect('/')

.. _job_chain:

Job chaining
------------

It is possible to chain several services together. For example one service
performs the pre-processing step, second performs the actual calculations while
third is responsible for post-preprocessing.

A job can obtain access to the output of other jobs as long as they are in
"Done" state and their IDs are known to the client. The IDs of input jobs
should be specified in the request JSON data using the "chain" key. The format
is a JSON list::

    "chain" : ["Service1_ID1", "Service2_ID2"]

The output of the requested jobs will be available in the working directory of
the new jobi. Each one in its own subdirectory. Upon job completion they will
be automatically removed. The subdirectory names can be accessed in the job
script via "@@{CIS_CHAIN*}" keywords. Where "*" corresponds to the position in
the "chain" list starting from 0.::

    cd @@{CIS_CHAIN0} # Output data of first input job
    cd ..
    cd @@{CIS_CHAIN1} # Output data of second input job

Verifying job status
--------------------

Job status can be queried by GET request on
http://app-gw.cis.gov.pl/api/status/[id]. Where [id] is the Job ID returned
during submission. The request returns one of:

* Waiting - Job is waiting for validation by AppServer
* Queued - Job is submitted to PBS and awaiting in queue
* Running - Job is performing calculations
* Closing - Job has finished computations and is waiting for cleanup
* Cleanup - Job started the cleanup stage (extraction of results etc.)
* Done - Job has finished successfully
* Failed - Job has finished with non zero exit code. The exit code is returned
  along with the status message e.g.: "Failed:127"
* Aborted - Job execution was aborted due to an error - either malformed job
  request or internal AppGateway/AppServer error. The type of error is returned
  alongside the status message e.g.: 
  "Aborted:-94 @Validator - Not supported variable: bad_variable"
* Killed - Job was killed either by the user or by the underlying queue system.
  The exit code is returned alonng with the status message e.g.:
  "Killed:271 Job was killed by the scheduler"

Example implementation in python::

    import requests
    import flask

    def status():
        # Get the Job ID from web browser cookie
        _jid = flask.request.cookies.get('CISMultiNestJobID')
        # Job ID stored - check status
        if _jid is not None:
            url = "http://app-gw.cis.gov.pl/api/status/" + _jid
            r = requests.get(url)
            return r.text

        return "No job submitted yet ..."

Exit codes
++++++++++

* Value 0 corresponds to successful execution
* Large negative values <-100,-90> correspond to errors encountered by the CIŚ AppServer:

  * -100: Undefined - this should not happen
  *  -99: Abort - default job abort exit code
  *  -98: Shutdown - Server shutdown
  *  -97: Delete - User delete request
  *  -96: UserKill - User kill request
  *  -95: SchedulerKill - Job killed by Scheduler
  *  -94: Validate - Validator error

* Small negative values <-10,-1> corrspond to scheduler errors:

  * -1: JOB_EXEC_FAIL1    - job exec failed, before files, no retry
  * -2: JOB_EXEC_FAIL2    - job exec failed, after files, no retry
  * -3: JOB_EXEC_RETRY    - job execution failed, do retry
  * -4: JOB_EXEC_INITABT  - job aborted on MOM initialization
  * -5: JOB_EXEC_INITRST  - job aborted on MOM init, chkpt, no migrate
  * -6: JOB_EXEC_INITRMG  - job aborted on MOM init, chkpt, ok migrate
  * -7: JOB_EXEC_BADRESRT - job restart failed
  * -8: JOB_EXEC_CMDFAIL  - exec() of user command failed

* Positive values <1,255> correspond to exit code of the application executed
  inside the job. By convention values <1-127> are used by the application to
  indicate the encountered error. Values <128-255> correspond to a signal which
  killed the application e.g. for signal 9 this would be 128+9=137.

* Positive values >= 256 correspond to the signal used by the scheduler to kill
  the job.

Job output
----------

The http base URL for the output files is retrieved as
http://app-gw.cis.gov.pl/api/output/[id]

Job progress
------------

If service supports a job can be queried about it's current progress:
http://app-gw.cis.gov.pl/api/progress/[id]

Job stop
--------

Job execution can be terminated. It will finish with a "Killed" status. The
produced output will be made available for user access. Kill request URL:
http://app-gw.cis.gov.pl/api/kill/[id]

Job removal
-----------

Job can be scheduled for removal. If a job is queued or running its execution
by the queue system will be stopped. All files related with the job will be
removed. Delete request URL: http://app-gw.cis.gov.pl/api/delete/[id]

Supported services
------------------

* Test

  + A : int(0,10000)
  + B : float(-100,100)
  + C : ["alpha", "beta", "gamma", "delta"]

* MultiNest

