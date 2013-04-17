=======
Web API
=======

CIŚ WebService REST API

Job submission
--------------

Jobs are subbited via POST request on http://appgate.cis.gov.pl/submit.
The POST request should contain job attributes either in JSON format or as
FORM data. The data payload should contain key value pairs corresponding to
variables supported by the service. In addition a reserved "service" keyword is
required with name of the service as a value.::

    {
        "service" : "MultiNest",
        "live_points" : 100
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
        url = "http://appgate.cis.gov.pl/submit"
        # The data will be sent as JSON payload
        headers = {'content-type': 'application/json'}
        # Send the POST request
        try:
            r = requests.post(url, data=json.dumps(payload), headers=headers)
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

Verifying job status
--------------------

Job status can be queried by GET request on
http://appgate.cis.gov.pl/status/[id]. Where [id] is the Job ID returned
during submission. The request returns one of:

* Waiting - Job is waiting for validation by AppServer
* Queued - Job is submitted to PBS and awaiting in queue
* Running - Job is performing calculations
* Done - Job has finished successfuly
* Failed - Job has finished with non zero exit code. The exit code is returned
  along with the status message e.g.: "Failed: 127"
* Aborted - Job execution was aborted due to an error - either malformed job
  request or internal AppGateway/AppServer error. The type of error is returned
  alongside the status message e.g.: "Aborted: @Validator - Not supported variable: bad_variable"
* Killed - Job was killed by the user.

Example implementation in python::

    import requests
    import flask

    def status():
        # Get the Job ID from web browser cookie
        _jid = flask.request.cookies.get('CISMultiNestJobID')
        # Job ID stored - check status
        if _jid is not None:
            url = "http://appgate.cis.gov.pl/status/" + _jid
            r = requests.get(url)
            return r.text

        return "No job submitted yet ..."

Job output
----------

The http base URL for the output files is retrieved as
http://appgate.cis.gov.pl/output/[id]

Job removal
-----------

Job can be scheduled for removal. If a job is queued or running its execution
by the queue system will be stopped. All files related with the job will be
romoved. Delete request URL: http://appgate.cis.gov.pl/delete/[id]

Supported services
------------------

* Test

  + A : int(0,10000)
  + B : float(-100,100)
  + C : ["alpha", "beta", "gamma", "delta"]

* MultiNest

  + argument : float(-10,10)
  + live_points : int(0,10000)
  + function : ["sin", "cos", "log"]

