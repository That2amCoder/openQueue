ids = [];
// Add a submit event listener to the form
$("form").submit(function(event) {
// Prevent the default form submission behavior
event.preventDefault();

// Get the values of the form and put them in a json of {'idx': value, 'idy}
var values = {};
ids.forEach(function(id) {
// convert the id to a string
values[id] = $("#" + id).val();
});
var values = JSON.stringify(values);
// Make a POST request to the /addentry endpoint with the form values
// The request should contain { 'data': {'1': value, '2': value, ..}}
$.post("/public/addentry", { 'data': values }, function(data) {
// Show the queue number in the page
$("#queue-number").show();
$('#questionPopoutSubmit').modal('show'); 

$("#queue-number-value").text(data.id);

$('form').get(0).reset()
});
});

// On page load, query the server for the form values
$.get("/public/info", function(data) {
// For each item in the 'forms' array, add a new form to the page
data.forms.forEach(function(form) {
// If the type is 0, it's a text input
if (form.type == 0) {
// Create a new text input in the format of:
// Text
// Subtext
// Input

// Make form group div;
var formGroup = $(`<div class="form-group"></div>`);

// Create the text element
var text = $(`<label for="${form.id}">${form.text}</label>`);
// Create the subtext element
var subtext = $(`<small class="text-muted">${form.subtext}</small>`);
// Create the input element
var input = document.createElement("input");
input.type = "text";
input.className = "form-control";
input.id = form.id;
input.placeholder = form.text;
// Append the elements to the form
formGroup.append(text);
formGroup.append(input);
formGroup.append(subtext);

$("#queue-form").append(formGroup);
// Add to the ids array
ids.push(form.id);
}
// If the type is 1, it's a textarea
else if (form.type == 1) {
// Create a new textarea in the format of:
// Text
// Subtext
// Input

// Create the text element
var text = document.createElement("h5");
text.innerHTML = form.text;
// Create the subtext element
var subtext = document.createElement("p");
subtext.innerHTML = form.subtext;
// Create the input element
var input = document.createElement("textarea");
input.className = "form-control";
input.id = form.id;
input.placeholder = form.placeholder;
// Append the elements to the form
$("#queue-form").append(text);
$("#queue-form").append(subtext);
$("#queue-form").append(input);
// Add to the ids array
ids.push(form.id);
}

// If the type is 2, it's a checkbox
else if (form.type == 2) {
// Create a new checkbox in the format of:
// Input
// Text

// Create the input element
var input = document.createElement("input");
input.type = "checkbox";
input.className = "form-check-input";
input.id = form.id;
// Create the text element
var text = document.createElement("label");
text.className = "form-check-label";
text.innerHTML = form.text;
// Append the elements to the form
$("#queue-form").append(input);
$("#queue-form").append(text);
// Add to the ids array
ids.push(form.id);
}
});
submit_button = '<input class="btn btn-block" type="submit" value="Submit">'
$("#queue-form").append(submit_button);
});
