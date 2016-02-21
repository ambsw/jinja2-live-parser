$(document).ready(function(){
    $('.convert').click(function() {
        // Push the input to the Jinja2 api (Python)
        $.post('/convert', {
            macros: $('#macros').val(),
            template: $('#template').val(),
            values: $('#values').val(),
            xmlformat: $('input[name="xmlformat"]').is(':checked') ? 1:0,
            strictformat: $('input[name="strictformat"]').is(':checked') ? 1:0
        }).done(function(json_response) {
            console.log(json_response);
            var response = JSON.parse(json_response);
            $('#render').html(response['render'] || "");
            $('#values-error').html(response['values-error'] || "");
            $('#macros-error').html(response['macros-error'] || "");
            $('#template-error').html(response['template-error'] || "");
            $('#render-error').html(response['render-error'] || "");

            // Grey out the white spaces chars if any
            //response = response.replace(/•/g, '<span class="whitespace">•</span>');

            // Display the answer
            $('#render').html(response['render'] || "");
        });
    });
});
