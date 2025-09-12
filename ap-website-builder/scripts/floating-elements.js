$(document).ready(function() {
    adjustMenuMarginBottom();
    adjustFooterVerticalOffset();
    fixMobileMenuWidth();
});

window.addEventListener('scroll', () => {
    adjustFooterVerticalOffset();
    fixMobileMenuWidth();
});

window.addEventListener('resize', () => {
    adjustMenuMarginBottom();
    adjustFooterVerticalOffset();
    fixMobileMenuWidth();
});

function adjustFooterVerticalOffset() {
    var copyrightDiv = document.getElementById("footer");
    var footerBarDiv = document.getElementById("footer-bar");
    if (footerBarDiv.classList.contains("floating")) {
        var copyrightDivY = copyrightDiv.getBoundingClientRect().y;
        var footerBarDivY = footerBarDiv.getBoundingClientRect().y;
        if (copyrightDivY <= footerBarDivY) {
            footerBarDiv.classList.remove("floating");
            footerBarDiv.classList.add("anchored");
        }
    } else {
        var footer = document.getElementById("footer");
        var footerHeight = footer.getBoundingClientRect().height;

        // https://stackoverflow.com/a/37934154
        var body = document.body, html = document.documentElement;
        var docHeight = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight,  html.scrollHeight, html.offsetHeight);
        if (pageYOffset <= docHeight - window.innerHeight - footerHeight) {
            footerBarDiv.classList.remove("anchored");
            footerBarDiv.classList.add("floating");
        }
    }
}

function adjustMenuMarginBottom() {
    var footerBarDiv = document.getElementById("footer-bar");
    var copyrightDiv = document.getElementById("copyright");
    var footerHeight = footerBarDiv.offsetHeight + copyrightDiv.offsetHeight;
    var mainArticle = document.getElementById("main-article");
    mainArticle.style.marginBottom = footerHeight + "px";
}

function fixMobileMenuWidth() {
    var topbarWidth = document.body.offsetWidth;
    var menuWidth = document.getElementById("header-row").offsetWidth;
    var topbar = document.getElementById("topbar");
    topbar.style.width = menuWidth + "px"
    topbar.style.marginLeft = ((topbarWidth - menuWidth) / 2) + "px";
}
