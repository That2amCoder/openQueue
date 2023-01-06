$(function() {
    var ids = [];
    var forms = {};

    function updateInfo() {
      //Make a get request to /public/info
      $.getJSON("/public/info", function(data) {
        // For each item in the 'forms' array, add a new form to the page
        data.forms.forEach(function(form) {
          // Add the form to the forms dict
          ids.push(form.id);
          forms[form.id] = form.text;
          updateEntry();
        });

      });
    }
    function updateEntry() {
      $.getJSON("/private/handler/getnext", function(data) {
        var entry = data.entry;

        var id = entry.id;
        var queueId = entry.queue_id;
        var timestamp = entry.timestamp;
        var status = entry.status;
        var handlerName = entry.handler_name;
        // Caclulate the time since the entry was created. The timestamp is EPOC time in seconds
        var timeSince = Date.now() - (timestamp * 1000);
        // convert it to minutes
        var minutes = Math.floor(timeSince / 60000);

        var entryHtml = "<div class='entry card' id='entry-" + id + "'>" 
        

        // Iterate through the ids array and add the form data to the entry
        entry.data = JSON.parse(entry.data);
        ids.forEach(function(id) {
          entryHtml += "<p><b>" + forms[id] + "</b>: " + entry.data[id] + "</p>";
        });
        

        entryHtml += "<h6 class='card-subtitle mb-2 text-muted'>"+minutes+" minutes ago</h6>"+
                    "<div class='btn-group' role='group'>"+ 
                    "<button id='" + id + "' class='btn ghost-button'>Ghost</button>"+
                    "<button id='" + id + "' class='btn in-progress-button'>In Progress</button>"+
                    "<button id='" + id + "' class='btn finished-button'>Finished</button>"+"</div>";
        
        $("#entry").html(entryHtml);
      });
    }

    // Update the entry on page load
    updateInfo();
    updateEntry();

    // Update the entry's status when the buttons are clicked using their class
    $("#entry").on("click", ".ghost-button", function() {
      updateEntryStatus(-1, $(this).attr("id"));
    });
    $("#entry").on("click", ".in-progress-button", function() {
      updateEntryStatus(1, $(this).attr("id"));
    });
    $("#entry").on("click", ".finished-button", function() {
      updateEntryStatus(2, $(this).attr("id"));
    });

    // Update the entry's status
    function updateEntryStatus(newStatus, id) {
      //Grab the ID of the button that was clicked
      console.log("ID : " + id);
      $.ajax({
        url: "/private/handler/updatestatus",
        type: "POST",
        data: {
          newStatus: newStatus,
          entryId: id
        },
        success: function() {
          if (newStatus == 2) {
            updateEntry();
          }
        }
      });
    }
  });