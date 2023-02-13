
$(function() {

  var ids = [];
  var forms = {};

  function updateInfo() {
    //Make a get request to /public/info
    $.getJSON("/public/info", function(data) {
      //Set the title of the page to the queue name
      $("title").html(data.name);
      //Add the information to the "info" div
      //The code should be represented as domain.com/join/code
      
      // Append the queue join link for handler's as domain.com/handler/code
      $("#info").html("<li class='nav-item'><a class='nav-link mx-3' href='/join/"+ data.code +"' target='_blank'>" + "<b>Add Entry</b>" + "</a></li>");
      $("#info").append("<li class='nav-item'><a class='nav-link mx-3' href='/join/handler/" + data.authcode + "' target='_blank'>" + "<b>Handler View</b>"+ "</a></li>");
      $("#info").append("<li class='nav-item'><a class='nav-link mx-3' href='/public/board' target='_blank'>" + "<b>Public Board</b>" +"</a></li>");
      
      // For each item in the 'forms' array, add a new form to the page
      data.forms.forEach(function(form) {
        // Add the form to the forms dict
        ids.push(form.id);
        forms[form.id] = form.text;
      });
      // Once the form metadata has been loaded, update the boxes
      updateBoxes();
      

    });
  }
  // Update the boxes on page load
  updateInfo();

  function updateBoxes() {
    $.getJSON("/private/getqueue", function(data) {
      var waitingBox = $("#waiting-box");
      var beingAnsweredBox = $("#being-answered-box");
      var answeredBox = $("#answered-box");

      // Clear the boxes
      waitingBox.html("");
      beingAnsweredBox.html("");
      answeredBox.html("");

      // Loop through the entries and add them to the appropriate box
      data.entries.forEach(function(entry) {
        var id = entry.id;
        var queueId = entry.queue_id;
        var name = entry.data;
        var timestamp = entry.timestamp;
        var status = entry.status;
        var handlerName = entry.handler_name;
        // Caclulate the time since the entry was created. The timestamp is EPOC time in seconds
        var timeSince = Date.now() - (timestamp * 1000);
        // convert it to minutes
        var minutes = Math.floor(timeSince / 60000);

        var entryHtml = "<div class='entry card' id='entry-" + id + "'>" +
                        "<h6 class='card-subtitle mb-2 text-muted'>"+minutes+" minutes ago</h6>" +
                        "<h5><span class='badge bg-danger'>"+handlerName+"</span></h5>";
        
        // For each id in the ids array, add the form data to the entry
        entry.data = JSON.parse(entry.data);
        ids.forEach(function(id) {
          entryHtml += "<p><b>" + forms[id] + "</b>: " + entry.data[id] + "</p>";
        });
        entryHtml += "</div>";
        


        if (status == 0) {
          waitingBox.append(entryHtml);
        } else if (status == 1) {
          beingAnsweredBox.append(entryHtml);
        } else if (status == 2) {
          answeredBox.append(entryHtml);
        }
      });


      // Make the entries draggable
      $(".entry").draggable({
        revert: "invalid",
        helper: "clone",
        start: function(event, ui) {
          $(this).css("visibility", "hidden");
          $(ui.helper).css("z-index", "9");
          // $(ui.helper).css('width', "33.33vw");
        },
        stop: function(event, ui){
          $(this).css("visibility", "visible");
        }
      });

      // Make the boxes droppable
      waitingBox.droppable({
        accept: ".entry",
        drop: function(event, ui) {
          var area = $(this).find(".box").html();
          var box = $(ui.draggable).html()
          
          $(ui.draggable).detach().css({
            top: 0,
            left: 0,
            visibility: "visible"
          }).appendTo(this);


          var entryId = ui.draggable.attr("id").split("-")[1];
          updateEntryStatus(entryId, 0);
        }
      });

      beingAnsweredBox.droppable({
        accept: ".entry",
        drop: function(event, ui) {
          var area = $(this).find(".box").html();
          var box = $(ui.draggable).html()
          
          $(ui.draggable).detach().css({
            top: 0,
            left: 0,
            visibility: "visible"
          }).appendTo(this);

          var entryId = ui.draggable.attr("id").split("-")[1];
          updateEntryStatus(entryId, 1);
        }
      });

      answeredBox.droppable({
        accept: ".entry",
        drop: function(event, ui) {
          var area = $(this).find(".box").html();
          var box = $(ui.draggable).html()
          
          $(ui.draggable).detach().css({
            top: 0,
            left: 0,
            visibility: "visible"
          }).appendTo(this);

          var entryId = ui.draggable.attr("id").split("-")[1];
          updateEntryStatus(entryId, 2);
        }
      });
    });
  }

  // Update the entry's status
  function updateEntryStatus(entryId, newStatus) {
    $.ajax({
      url: "/private/updatestatus",
      type: "POST",
      data: {
        entryId: entryId,
        newStatus: newStatus
      },
      success: function() {
        updateBoxes();
      }
    });
  }


  updateBoxes();
});

