function toggle_header(event, id) {
    $(id).toggle();
    if ($(id).is(':visible')) {
        $(event.target).text("Hide");
    } else {
        $(event.target).text("Show");
    }
}