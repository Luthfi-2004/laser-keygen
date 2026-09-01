// layout.js - Core script to inject components
document.addEventListener("DOMContentLoaded", async () => {
    // 1. Inject Sidebar
    const sidebarContainer = document.getElementById('layout-sidebar');
    if (sidebarContainer) {
        const res = await fetch('components/sidebar.html');
        const html = await res.text();
        const currentPage = sidebarContainer.getAttribute('data-active-page');
        sidebarContainer.outerHTML = html;
        
        // Mark active menu after injecting
        // We have to query the document again because sidebarContainer is replaced
        const newSidebar = document.querySelector('aside');
        if (newSidebar && currentPage) {
            const links = newSidebar.querySelectorAll('.nav-link');
            links.forEach(link => {
                link.classList.remove('active', 'text-gray-300');
                if(link.getAttribute('data-page') === currentPage) {
                    link.classList.add('active');
                    link.classList.remove('text-gray-600');
                }
            });
        }
    }

    // 2. Inject Topbar
    const topbarContainer = document.getElementById('layout-topbar');
    if (topbarContainer) {
        const res = await fetch('components/topbar.html');
        const html = await res.text();
        const pageTitle = topbarContainer.getAttribute('data-title');
        topbarContainer.outerHTML = html;
        
        // Update Title if needed
        if (pageTitle) {
            const titleEl = document.getElementById('topbar-title');
            if (titleEl) titleEl.innerText = pageTitle;
        }
    }

    // 3. Inject Footer
    const footerContainer = document.getElementById('layout-footer');
    if (footerContainer) {
        const res = await fetch('components/footer.html');
        const html = await res.text();
        footerContainer.outerHTML = html;
    }
});

// Expose theme toggle globally so topbar can call it
window.toggleTheme = function() {
    if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    }
}
