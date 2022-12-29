

$(function() {

  function updateInfo() {
    //Make a get request to /public/info
    $.getJSON("/public/info", function(data) {
      //Set the title of the page to the queue name
      $("title").html(data.name);
      //Add the information to the "info" div
      // The code should be represented as domain.com/join/code
      
      //First two links were broken for me
      // $("#info").html("Join the queue at <a href='" + window.location.href.split("/")[2] + "/join/" + data.code + "'>" + window.location.href.split("/")[2] + "/join/" + data.code + "</a>");
      // // Append the queue join link for handler's as domain.com/handler/code
      // $("#info").append("<br>Handlers can join the queue at <a href='" + window.location.href.split("/")[2] + "/join/handler/" + data.authcode + "'>" + window.location.href.split("/")[2] + "/join/handler/" + data.authcode + "</a>");
      // $("#info").append("<br>Public board can be found <a href='/public/board'>" + window.location.href.split("/")[2] + "/public/board</a>");
      
      $("#info").html("<a href='" + "/join/" + data.code + "'>" + "Add Entry" + "</a>");
      $("#info").append("<a href='" + "/join/handler/" + data.authcode + "'>" + "Handler View"+ "</a>");
      $("#info").append("<a href='/public/board'>" + "Public Board" +"</a>");

    });
  }
  
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

        var entryHtml = "<div class='entry' id='entry-" + id + "'>" + name + "<br>" + question +"<br>" + minutes + " minutes ago. <br> Handled by: <b>" + handlerName + "</b></div>";

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

  // Update the boxes every 30 seconds
  setInterval(updateBoxes, 10000);

  // Update the boxes on page load
  updateInfo();
  updateBoxes();
});

