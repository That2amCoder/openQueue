# OpenQueue

OpenQueue is an open source queue managment system to handle queues. Allows anybody with a web browser to enter the queue and fill in customizable parameters, and provides an administrative overview in handling it.

Also it provides a "handler" page, which automatically gathers the next item in the queue and serves it in order to manage it better.

## Features

- Administrative overview, allowing to track who has what ticket and manage tickets back and forth in terms of state
- Handler page, allowing for handlers to see the current ticket at hand and change the status
- A queue system, which allows users to enter their information with user-specified questions
- A public board page for people to easily know how to join the queue with a QR code
- Also the user knows how far they are in the queue

## Planned features:
- Statistics, such as number of handlers, average response rate
- Better customization and optimization

## Documentation

### /create

The /create takes the following parameters:  
`'title'`: The title of the queue  
`'description'`: The descpription of the queue  
`'display_current'`: whether to display the current number on the board  
```
'form': [
    { 
        "text": The text of the input 
        "subtext": The subtext of the input
        "type": (0 = text, 1 = multiple choice, 2 = checkbox, 3 = dropdown)
        "options": Options for 3, seperated by newlines
        "required": whether it is required
        "order": The order it appears starting from 0 being on the top
    }, ...
]
```

### Admin pages

![Creation page](https://i.imgur.com/WHMdhe3.png)

![Public board page](https://i.imgur.com/oIzeKc6.png)

![Administrative page](https://i.imgur.com/4BRquvv.png)

### Public pages
![Queue System Page](https://i.imgur.com/aiewA08.png)


