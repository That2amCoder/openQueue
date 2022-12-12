    // Retrieve information from /public/<int:id>/info
    fetch("/public/info")
      .then(response => response.json())
      .then(data => {
        // Update page elements with data from the response
        document.getElementById("title").innerHTML = data.title;
        document.getElementById("description").innerHTML = data.description;
        // set the code as domain.com/join/code
        document.getElementById("code").innerHTML = window.location.href.split("/")[2] + "/join/" + data.code;
        // Url encoded image from data.url
        document.getElementById("qr").src = "data:image/png;base64," + data.qr;  
      });