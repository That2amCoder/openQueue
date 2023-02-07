questionList = {'forms': []};
var x = 0;

// When the addQuestion button is clicked, call the addQuestion function using jquery
//when the document is ready
$(document).ready(function() {
    $("#addQuestion").click(function() {
        // Get the text, subtext, and form from the input fields
        var text = $("#question_title").val();
        var subtext = $("#question_subtitle").val();
        var type = $("#question_type").val();
        var required = $("#question_required").val();
        var options = $("#question_options").val();

        questionList.forms.push({'text': text, 'subtext': subtext, 'type': type, 'options': options, 'required': required, order: x});
        // add the entry to #questionList
        $("#questionList").append('<li class="list-group-item" id="' + x + '">' + text + ': ' + subtext + '</li>');
        // If its a dropdown or multiple choice, add the options
        x++;

        // Clear the input fields
        $("#question_title").val("");
        $("#question_subtitle").val("");
        $("#question_type").val("Text");
    });

    // Submit function
    $("#createQueueForm").submit(function(e) {
        e.preventDefault();
        var title = $("#title").val();
        var description = $("#description").val();
        var display_current = $("#display_current").val();
        // JSOnify the questionList
        questionListtxt = JSON.stringify(questionList);
        
        //Make a POST request to the server at /create with the form data
        $.post("/create", {title: title, description: description, display_current: display_current, questionList: questionListtxt}, function(data) {
            console.log(data);
        });
        // Set the site to /private/admin
        window.location.href = "/private/admin";
    });

    $("#question_type").change(function() {
        var type = $("#question_type").val();
        if (type == 2 || type == 4) {
            $("#question_options_div").show();
        } else {
            $("#question_options_div").hide();
        }
    });
});



function updateOrder() {
    // Get the order of the items in the questionList
    var order = $("#questionList").sortable("toArray");
    // Update the order of the items in the questionList
    questionList.forms = order;
}





