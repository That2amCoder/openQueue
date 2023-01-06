questionList = {'forms': []};
var x = 0;
// When the addQuestion button is clicked, call the addQuestion function using jquery
//when the document is ready
$(document).ready(function() {
    $("#addQuestion").click(function() {
        // Get the text, subtext, and form from the input fields
        var text = $("#formTitle").val();
        var subtext = $("#formSubtitle").val();
        var type = $("#formRichText").val();
        // Add the question to the questionList
        questionList.forms.push({'text': text, 'subtext': subtext, 'type': type, 'options': '', 'required': false, order: x});
        x++;
    });
});

// Submit function
function myfunction(e) {
    e.preventDefault();
    var title = $("#title").val();
    var description = $("#description").val();
    var display_current = $("#display_current").val();

    //Make a POST request to the server at /create with the form data
    $.post("/create", {title: title, description: description, display_current: display_current, questionList: questionList}, function(data) {
        console.log("AAAAAAA");
        console.log(data);
    });
    return false;
};
