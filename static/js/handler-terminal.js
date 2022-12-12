$(function() {
    function updateEntry() {
      $.getJSON("/private/handler/getnext", function(data) {
        var entry = data.entry;

        var id = entry[0];
        var queueId = entry[1];
        var name = entry[2];
        var question = entry[3];
        var extra = entry[4];
        var timestamp = entry[5];
        var status = entry[6];
        var handlerName = entry[7];
        // Caclulate the time since the entry was created. The timestamp is EPOC time in seconds
        var timeSince = Date.now() - (timestamp * 1000);
        // convert it to minutes
        var minutes = Math.floor(timeSince / 60000);
        var entryHtml = "<p class='entry-name'>" + name + "</p>" +
                        "<p>" + question + "</p>" +
                        "<p>" + extra + "</p>" +
                        "<p class='entry-time'>Submitted " + minutes + " minute(s) ago</p>";
        //Set the button IDs the same as the entry ID so that when the POST request happens, we know which entry to update
          entryHtml += "<button id='" + id + "' class='ghost-button'>Ghost</button>";
          entryHtml += "<button id='" + id + "' class='in-progress-button'>In Progress</button>";
          entryHtml += "<button id='" + id + "' class='finished-button'>Finished</button>";
          
        
        $("#entry").html(entryHtml);
      });
    }

    // Update the entry on page load
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