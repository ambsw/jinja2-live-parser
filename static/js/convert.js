$(document).ready(function(){
    $('.convert').click(function() {
        // Push the input to the Jinja2 api (Python)
        $.post('/convert', {
            template: $('#template').val(),
            values: $('#values').val(),
        }).done(function(json_response) {
            console.log(json_response);
            var response = JSON.parse(json_response);
            $('#values-error').html("");
            $('#template-error').html("");
            if ("values-error" in response)
                $('#values-error').html(response['values-error']);
            else
            if ("template-error" in response)
                $('#template-error').html(response['template-error']);

            // Grey out the white spaces chars if any
            //response = response.replace(/•/g, '<span class="whitespace">•</span>');

            // Display the answer
            $('#render').html(response['render']);
        });
    });
});
