var scrollFlag = false;

$(document).ready(function() {
    var menuLinks = document.getElementsByClassName("menu-button");

    for (var i=0; i < menuLinks.length; i++) {
        var aObj = menuLinks[i];
        aObj.onclick = function() {clickMenuButton();};
    }
});

$(window).scroll(function() {
  // Code to execute when the window is scrolled
  if (scrollFlag) {
    offsetNavbar();
    scrollFlag = false;
  }
});

function clickMenuButton() {
    var hamburgerButton = document.getElementById("mobile-hamburger");
    if (hamburgerButton.classList.contains("selected")) {
        hamburgerButton.click();
    }
    scrollFlag = true;
}

function offsetNavbar() {
    var isMobile = document.body.offsetWidth <= 768;
    var offset = 0;
    if (!isMobile) {
        var topbar = document.getElementById("topbar");
        offset = -topbar.offsetHeight * 1.2;
    } else {
        var headerRow = document.getElementById("header-row");
        offset = -headerRow.offsetHeight * 1.2;
    }
    window.scrollBy(0, offset);
}