$(document).ready(function() {
    copyFooterText();
    adjustMenuVerticalOffset();
    fixMobileMenuWidth();
    adjustFooterVerticalOffset();
});

window.addEventListener('scroll', () => {
    adjustMenuVerticalOffset();
    fixMobileMenuWidth();
    adjustFooterVerticalOffset();
});

window.addEventListener('resize', () => {
    adjustMenuVerticalOffset();
    fixMobileMenuWidth();
    adjustFooterVerticalOffset();
});

function copyFooterText() {
    var floatingFooterContents = document.getElementById("footer-bar").innerHTML;
    document.getElementById("footer-text").innerHTML = floatingFooterContents;
}

function adjustMenuVerticalOffset() {
    var mainArticle = document.getElementById("main-article");

    var isMobile = document.body.offsetWidth <= 768;
    if (!isMobile) {
        var topbar = document.getElementById("topbar");
        mainArticle.style.transform = "translateY(" + topbar.offsetHeight + "px)";
    } else {
        var headerRow = document.getElementById("header-row");
        mainArticle.style.transform = "translateY(" + headerRow.offsetHeight + "px)";
    }
}

function fixMobileMenuWidth() {
    var topbarWidth = document.body.offsetWidth;
    var menuWidth = document.getElementById("header-row").offsetWidth;
    var topbar = document.getElementById("topbar");
    topbar.style.width = menuWidth + "px"
    topbar.style.marginLeft = ((topbarWidth - menuWidth) / 2) + "px";
}

function adjustFooterVerticalOffset() {
    var footerAnchoredDiv = document.getElementById("footer-anchored");
    var footerBarDiv = document.getElementById("footer-bar");
    if (footerBarDiv.classList.contains("floating")) {
        var footerAnchoredDivY = footerAnchoredDiv.getBoundingClientRect().y;
        var footerBarDivY = footerBarDiv.getBoundingClientRect().y;
        console.log(footerAnchoredDivY + " ?<= " + footerBarDivY);
        if (footerAnchoredDivY <= footerBarDivY) {
            footerBarDiv.classList.remove("floating");
            footerBarDiv.classList.add("anchored");
            footerBarDiv.hidden = true;
            console.log("HIDDEN");
        }
    } else {
        var footer = document.getElementById("footer-anchored");
        var footerHeight = footer.getBoundingClientRect().height;

        // https://stackoverflow.com/a/37934154
        var body = document.body, html = document.documentElement;
        var docHeight = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight,  html.scrollHeight, html.offsetHeight);
        if (pageYOffset <= docHeight - window.innerHeight - footerHeight) {
            footerBarDiv.classList.remove("anchored");
            footerBarDiv.classList.add("floating");
            footerBarDiv.hidden = false;
            console.log("SHOWN");
        }
    }
}
