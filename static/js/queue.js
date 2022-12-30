 // Add a submit event listener to the form
 $("form").submit(function(event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Get the values of the form inputs
    var name = $("#name-input").val();
    var question = $("#question-input").val();
    var extra = $("#extra-input").val();
    // Make a POST request to the /addentry endpoint with the form values
    // The currentl url is /ID/public, the target url is /ID/addentry
    $.post("/public/addentry", { name: name, question: question, extra: extra }, function(data) {
      // Show the queue number in the page
      $("#queue-number").show();
      $('#questionPopoutSubmit').modal('show'); 

      $("#queue-number-value").text(data.id);

      $('form').get(0).reset()

      // Hide the form
      // $("form").hide();
    });
  });