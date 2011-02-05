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
                    console.log(data);
                });
        } else {
            console.log('no message');
        }
        return false;
    });
    
    
    
    
})
