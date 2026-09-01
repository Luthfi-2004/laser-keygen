window.initApp = async function(injectSidebar = true) {
    // 1. Inject Sidebar
    if (injectSidebar) {
        const sidebarContainer = document.getElementById('layout-sidebar');
        if (sidebarContainer) {
            const res = await fetch('components/sidebar.html');
            const html = await res.text();
            const currentPage = sidebarContainer.getAttribute('data-active-page');
            sidebarContainer.outerHTML = html;
            
            const newSidebar = document.querySelector('aside');
            if (newSidebar && currentPage) {
                const links = newSidebar.querySelectorAll('.nav-link');
                links.forEach(link => {
                    link.classList.remove('active', 'text-gray-300');
                    if(link.getAttribute('data-page') === currentPage) {
                        link.classList.add('active');
                        link.classList.remove('text-gray-600');
                    } else {
                        link.classList.add('text-gray-600');
                    }
                });
            }
        }
    }

    // 2. Inject Topbar
    const topbarContainer = document.getElementById('layout-topbar');
    if (topbarContainer) {
        const res = await fetch('components/topbar.html');
        const html = await res.text();
        const pageTitle = topbarContainer.getAttribute('data-title');
        topbarContainer.outerHTML = html;
        
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
};

// SPA Router
if (!window._routerAttached) {
    window._routerAttached = true;
    
    document.addEventListener('click', async (e) => {
        const link = e.target.closest('a');
        // Only intercept local .html links (or root /)
        if (link && link.href && link.origin === location.origin && (link.pathname.endsWith('.html') || link.pathname === '/')) {
            // Ignore download links
            if (link.hasAttribute('download')) return;
            
            e.preventDefault();
            navigateTo(link.pathname);
        }
    });

    window.addEventListener('popstate', () => {
        navigateTo(location.pathname, false);
    });
}

async function navigateTo(path, push = true) {
    // Determine page name from path for sidebar highlighting
    let pageName = path.split('/').pop().replace('.html', '');
    if (!pageName || pageName === '') pageName = 'index';

    // Update sidebar active state immediately
    const sidebarLinks = document.querySelectorAll('aside .nav-link');
    sidebarLinks.forEach(l => {
        l.classList.remove('active', 'text-gray-300');
        if (l.getAttribute('data-page') === pageName) {
            l.classList.add('active');
            l.classList.remove('text-gray-600');
        } else {
            l.classList.add('text-gray-600');
        }
    });

    // Start view transition or just fade out
    document.body.style.transition = 'opacity 0.2s';
    document.body.style.opacity = '0.4';
    
    try {
        const res = await fetch(path);
        const html = await res.text();
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        const newMain = doc.querySelector('main');
        const oldMain = document.querySelector('main');
        
        if (newMain && oldMain) {
            oldMain.parentNode.replaceChild(newMain, oldMain);
            document.title = doc.title;
            if (push) {
                history.pushState(null, '', path);
            }
            
            // Re-inject Topbar & Footer inside the new main
            await window.initApp(false);
            
            // Re-execute all inline scripts and specific logic for the new page
            const scripts = doc.body.querySelectorAll('script');
            scripts.forEach(script => {
                if (!script.src || !script.src.includes('layout.js')) {
                    const newScript = document.createElement('script');
                    if (script.src) newScript.src = script.src;
                    else newScript.textContent = script.textContent;
                    document.body.appendChild(newScript);
                }
            });
            
            // Dispatch a custom event so page-specific scripts know it's loaded
            document.dispatchEvent(new Event('DOMContentLoaded')); 
            // Note: DOMContentLoaded is read-only, but we can trigger custom logic if needed. 
            // Our inline scripts in index and history currently rely on DOMContentLoaded.
            // We need to make sure they run! 
            // Actually, adding the script to the DOM directly executes it immediately, but event listeners for DOMContentLoaded won't fire again.
            // Let's manually trigger DOMContentLoaded listeners in those scripts? 
            // Wait, we can't manually trigger the native DOMContentLoaded easily on document.
            // We should dispatch a custom 'spa:loaded' event or similar, or just fire a regular Event('DOMContentLoaded').
        }
    } catch (e) {
        console.error('Navigation error:', e);
        window.location.href = path; // fallback
    } finally {
        document.body.style.opacity = '1';
    }
}

// Initial load
if (document.readyState === 'loading') {
    document.addEventListener("DOMContentLoaded", () => window.initApp(true));
} else {
    window.initApp(true);
}

// Global Theme Toggle
window.toggleTheme = function() {
    if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    }
}

// We need to patch the scripts in index.html and history.html to listen to a custom event or just execute.
