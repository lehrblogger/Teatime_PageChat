$(document).ready(function() {
    
    
    
    $("form").submit(function() {
        var text = $('form input:first').val();
        if (text != '') {
            console.log(text);
            $.post('message', 
                {
                    text: text,
                    url: $('a.conver_url').html()
                },
                function(data) {
                    console.log("message sent");
                }
            );
        } else {
            console.log('no message');
        }
        $('form input:first').val('');
        return false;
    });

    onOpened = function() {
        $.post('opened', 
            {
                url: $('a.conver_url').html()
            },
            function(data) {
                console.log('channel opened');
            }
        );
    };
    
    onClosed = function() {
        $.post('closed', 
            {
                url: $('a.conver_url').html()
            },
            function(data) {
                console.log('channel closed');
            }
        );
    };
    
    onMessage = function(m) {
        console.log(m);
        var new_message = JSON.parse(m.data);
        $('ul#messages').append('<li><strong>' + new_message.author + ':</strong> ' + new_message.message + '</li>')
    }
    
    openChannel = function() {
        console.log('token');
        var channel = new goog.appengine.Channel(token);
        var handler = {
            'onopen': onOpened,
            'onmessage': onMessage,
            'onerror': function() {},
            'onclose': onClosed
        };
        var socket = channel.open(handler);
        socket.onopen = onOpened;
        socket.onmessage = onMessage;
    }

    setTimeout(openChannel, 100);
    
})
