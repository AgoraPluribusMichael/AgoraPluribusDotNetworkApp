document.addEventListener('DOMContentLoaded', function() {
    var sectionHeaders = document.getElementsByClassName("section-header");
    var tocBodyObj = document.getElementById("toc-body");

    var maxWidth = 0;

    for (var i=0; i < sectionHeaders.length; i++) {
        var header = sectionHeaders[i];
        var id = header.id;
        var label = document.getElementById(id).innerText;

        var liObj = document.createElement("li");
        var aObj = document.createElement("a");
        aObj.href = "#" + id;
        aObj.innerText = label;
        aObj.classList.add("toc-label");
        aObj.onclick = function() {offsetNavbar();};
        liObj.appendChild(aObj);
        tocBodyObj.appendChild(liObj);

        var width = aObj.offsetWidth;
        if (width > maxWidth) {
            maxWidth = width;
        }
    }
});

function offsetNavbar() {
    var topbar = document.getElementById("topbar");
    if (topbar.classList.contains("fixed")) {
        var offset = topbar.offsetHeight;
        window.scrollBy(0, offset);
    }
}