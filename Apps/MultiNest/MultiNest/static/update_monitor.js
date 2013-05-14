// Script that checks current job progress log and displays it
// Script based on jQuery

$(document).ready(function(){
    console.log("SetupMonitor")
    function updateMonitor() {
        console.log("UpdateMonitor:" + current_state)
        // The current_state is set by updateStatus function loaded in
        // layout.html. Check for updates only for jobs that did not finish
        // (states 1-3)
        if(current_state >= 4) {
            return false;
        }

        // Query server for progress info
        $.getJSON($SCRIPT_ROOT + '/progress',
            function(data) {
                // Clear contents
                $("#job_output").text("");
                // Set new contents - using append as it does not escape
                // html tags
                $("#job_output").append(data.job_output.split("\n").join("<br />"));
                $("#job_output").scrollTop($("#job_output")[0].scrollHeight);
            });
    };

    // We do not actually update progress on page load. It will be loaded by template anyway.
    //updateMonitor();
    setInterval(updateMonitor, 5000); // 5 * 1000 miliseconds
});
