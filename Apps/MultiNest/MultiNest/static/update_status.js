// Script that checks current job state and updates state boxes
// Script based on jQuery

// Current job state
var current_state = 0

$(document).ready(function(){
    function updateStatus() {
        // Perform updates only for jobs in queued or running state
        if(current_state >= 4) {
            return false;
        }

        // Query server for job state
        $.getJSON($SCRIPT_ROOT + '/status',
            function(data) {
                // Adjust colors of state boxes
                if(data.state == 1) {
                    $("#status").attr("class",data.type);
                    $("#messages").hide();
                } else {
                    $("#status").attr("class",data.type);
                    $("#messages").attr("class",data.type);
                    $("#messages").show();
                };
                // Adjust contents of state boxes
                $("#status").text(data.desc);
                $("#messages").text(data.msg);

                // Update job state
                if(current_state != data.state) {
                    current_state = data.state;
                }
            });
    };

    // We do not actually update status on page load. It will be loaded by template anyway.
    //updateStatus();
    // Update job state every 5s
    setInterval(updateStatus, 5000); // 5 * 1000 miliseconds
});

