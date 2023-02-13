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
    $.post("/public/addentry", {
        'data': values
    }, function(data) {
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
            formGroup.append(subtext);
            formGroup.append(input);

            $("#queue-form").append(formGroup);
            // Add to the ids array
            ids.push(form.id);
        }// If the type is 1, it's a textarea
        else if (form.type == 1) {
            // Create a new textarea in the format of:
            // Text
            // Subtext
            // Input

            var formGroup = $(`<div class="form-group"></div>`);
            var text = $(`<label for="${form.id}">${form.text}</label>`);
            var subtext = $(`<small class="text-muted">${form.subtext}</small>`);
            var textarea = document.createElement("textarea");

            textarea.type = "text";
            textarea.className = "form-control";
            textarea.id = form.id;
            textarea.placeholder = form.text;

            formGroup.append(text);
            formGroup.append(subtext);
            formGroup.append(textarea);

            $("#queue-form").append(formGroup);
            ids.push(form.id);
        }
        // If the type is 2, it's a checkbox
        else if (form.type == 2) {
            // Create a new checkbox in the format of:
            // Input
            // Text

            var formGroup = $(`<div class="form-group"></div>`);

            // Append the elements to the form
            formGroup.append(`<label class="form-check-label">
                  <input id="${form.id}" type="checkbox" value="">${form.text}
                  </label>`);
            $("#queue-form").append(formGroup);
            // Add to the ids array
            ids.push(form.id);
        }
        // If the type is 3 it's a Multiple Choice
        else if (form.type == 3) {
            // Create a new Multiple Choice in the format of:
            // Text
            // Subtext
            // Input

            var formGroup = $(`<div class="form-group"></div>`);
            var text = $(`<label for="${form.id}">${form.text}</label><br>`);
            var subtext = $(`<small class="text-muted">${form.subtext}</small>`);


            formGroup.append(text);
            formGroup.append(subtext);


            // Add to the ids array
            ids.push(form.id);

           // Options are seperated by new lines. For multiple choice, each option is a checkbox in a list
            var options = form.options.split("\n");
            options.forEach(function(option) {
                formGroup.append(`<label class="form-check-label"` + `for="${form.id}">` + `<input id="${form.id}" type="checkbox" value="">${option}` + `</label>`);
            });            
            $("#queue-form").append(formGroup);

        }
        // If the type is 4 it's a Dropdown
        else if (form.type == 4) {

            var formGroup = $(`<div class="form-group"></div>`);
            var text = $(`<label for="${form.id}">${form.text}</label><br>`);
            var subtext = $(`<small class="text-muted">${form.subtext}</small>`);
            var select = document.createElement("select");
            select.className = "form-control";
            select.id = form.id;

            formGroup.append(text);
            formGroup.append(subtext);

            // Add to the ids array
            ids.push(form.id);

            // Options are seperated by new lines.
            var options = form.options.split("\n");
            options.forEach(function(option) {
                select.innerHTML += `<option>${option}</option>`;
            });
            formGroup.append(select);
            $("#queue-form").append(formGroup);
        }

    });
    submit_button = '<input class="btn btn-block" type="submit" value="Submit">'
    $("#queue-form").append(submit_button);
});
