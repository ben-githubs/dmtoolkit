function populateSubclassSelector() {
    class_name = $('#class_').val();

    $.ajax({
        url: `/api/classes/${class_name}/subclasses`,
        method: 'GET',
        success: function(response) {
            $('#subclass').empty();
            data = $.parseJSON(response);
            $.each(data, function (index, item) {
                $('#subclass').append(`<option value=${index}>${item}</option>`)
            })
        }
    })
}