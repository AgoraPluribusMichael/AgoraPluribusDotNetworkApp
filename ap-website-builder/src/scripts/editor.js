$(document).ready(function() {
    var panelObjs = document.getElementsByClassName("panel");

    for (var i=0; i < panelObjs.length; i++) {
        var panel = panelObjs[i];
        var editButton = document.createElement("BUTTON");
        editButton.innerText = "Edit";
    }
});