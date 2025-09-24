document.addEventListener('DOMContentLoaded', () => {
    const pathnameComps = window.location.pathname.split('/');
    const editorIndex = pathnameComps.indexOf("editor");
    siteId = pathnameComps[editorIndex-1];
    pageId = pathnameComps[editorIndex+1];
    pageId = pageId.split('.')[0];
});

async function loadMenuButtons(siteId, pageId) {
//     <!-- @target #topbar:child -->
    // <a href="${BUTTON_HREF}" class="menu-button">${BUTTON_LABEL}</a>
    const topbar = document.getElementById("topbar");
    const response = await fetch(`http://127.0.0.1:8000/api/v1/sites/${siteId}/pages/${pageId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    const pages = await response.json();
    console.log(pages["pages"]);
}