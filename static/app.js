/**
 * app.js - Quran Index Static Site
 *
 * Handles:
 * - Loading sidebar nav from category/index.json
 * - Hash-based routing (e.g. #jannat, #adam)
 * - Fetching and rendering .md files from category/
 * - Mobile menu toggle & sidebar scroll persistence
 */

// ─── Sidebar ──────────────────────────────────────────────────────────────────

/**
 * Loads the sidebar navigation from category/index.json.
 * @param {string|null} activeSlug - The currently active category slug, or null.
 */
function loadSidebar(activeSlug) {
  fetch('category/index.json')
    .then(res => {
      if (!res.ok) throw new Error('Failed to load category index');
      return res.json();
    })
    .then(categories => {
      const navList = document.getElementById('nav-list');
      if (!navList) return;

      navList.innerHTML = '';

      categories.forEach(cat => {
        const li = document.createElement('li');
        if (cat.slug === activeSlug) {
          li.className = 'veg';
        }

        const a = document.createElement('a');
        a.className = 'link';
        a.href = 'index.html#' + cat.slug;
        a.textContent = cat.title;

        // Close mobile menu on link click
        a.addEventListener('click', () => {
          if (window.innerWidth <= 815) {
            document.getElementById('navbar').classList.remove('open');
          }
        });

        li.appendChild(a);
        navList.appendChild(li);
      });

      // Restore sidebar scroll position
      restoreSidebarScroll();
    })
    .catch(err => {
      console.error('Sidebar load error:', err);
      const navList = document.getElementById('nav-list');
      if (navList) {
        navList.innerHTML = '<li><a href="#">লোড করতে সমস্যা হয়েছে</a></li>';
      }
    });
}

// ─── Auto-Ayat Styling ────────────────────────────────────────────────────────

/**
 * After markdown is rendered, automatically wraps the paragraph content
 * that sits below each ## (h2) heading inside a <div class="ayat">.
 *
 * This means you NEVER need to write <div class="ayat"> in your .md files.
 * Just write your text under a ## heading and it will be styled automatically.
 *
 * @param {HTMLElement} container - The article element containing rendered HTML
 */
function applyAyatStyling(container) {
  const children = Array.from(container.childNodes);
  container.innerHTML = '';

  let currentGroup = null;

  children.forEach(node => {
    const isHeading = node.nodeType === Node.ELEMENT_NODE &&
      ['H1', 'H2', 'H3'].includes(node.tagName);

    const isAyatDiv = node.nodeType === Node.ELEMENT_NODE &&
      node.tagName === 'DIV' && node.classList.contains('ayat');

    if (node.nodeType === Node.TEXT_NODE && node.textContent.trim() === '') {
      return;
    }

    if (isHeading) {
      if (currentGroup && currentGroup.innerHTML.trim() !== '') {
        container.appendChild(currentGroup);
      }
      currentGroup = null;
      container.appendChild(node.cloneNode(true));
      currentGroup = document.createElement('div');
      currentGroup.className = 'ayat';
    } else if (isAyatDiv) {
      if (currentGroup && currentGroup.innerHTML.trim() !== '') {
        container.appendChild(currentGroup);
      }
      currentGroup = null;
      container.appendChild(node.cloneNode(true));
    } else {
      if (currentGroup) {
        currentGroup.appendChild(node.cloneNode(true));
      } else {
        container.appendChild(node.cloneNode(true));
      }
    }
  });

  if (currentGroup && currentGroup.innerHTML.trim() !== '') {
    container.appendChild(currentGroup);
  }
}

// ─── Markdown Content ─────────────────────────────────────────────────────────

/**
 * Loads and renders a markdown file for the given slug.
 * @param {string} slug - Category slug matching a file in category/
 * @param {string} title - Category title for the page header
 */
function loadCategory(slug, title) {
  const contentEl = document.getElementById('page-content');
  const titleEl = document.getElementById('page-title');

  if (contentEl) contentEl.innerHTML = '<p style="color:#999;font-size:0.9em;">লোড হচ্ছে...</p>';
  if (titleEl) titleEl.textContent = title || '';

  // Update page title
  document.title = (title ? title + ' - ' : '') + 'বিষয় ভিত্তিক আয়াত';

  fetch('category/' + slug + '.md')
    .then(res => {
      if (!res.ok) throw new Error('File not found: ' + slug + '.md');
      return res.text();
    })
    .then(mdText => {
      if (contentEl) {
        marked.setOptions({ breaks: true });
        contentEl.innerHTML = marked.parse(mdText);
        // Auto-wrap content under headings with .ayat styling
        applyAyatStyling(contentEl);
      }
      if (titleEl) titleEl.textContent = title || slug;

      // Scroll main content to top
      const mainDoc = document.getElementById('main-doc');
      if (mainDoc) mainDoc.scrollTop = 0;
      window.scrollTo(0, 0);
    })
    .catch(err => {
      console.error('Content load error:', err);
      if (contentEl) {
        contentEl.innerHTML = '<p style="color:#c00;">কন্টেন্ট লোড করতে সমস্যা হয়েছে।</p>';
      }
    });
}


// ─── Routing ──────────────────────────────────────────────────────────────────

let categoriesCache = null;

/**
 * Reads the current URL hash and loads the appropriate category.
 * Falls back to the first category (jannat) if no hash is set.
 */
function handleRoute() {
  const hash = window.location.hash.replace('#', '').trim();

  if (!categoriesCache) {
    fetch('category/index.json')
      .then(res => res.json())
      .then(cats => {
        categoriesCache = cats;
        routeToSlug(hash, cats);
      })
      .catch(() => {
        routeToSlug(hash, []);
      });
  } else {
    routeToSlug(hash, categoriesCache);
  }
}

function routeToSlug(hash, categories) {
  let target = categories.find(c => c.slug === hash);

  // Default: first category (jannat)
  if (!target && categories.length > 0) {
    target = categories[0];
    // Update URL hash without triggering another route event
    history.replaceState(null, '', '#' + target.slug);
  }

  if (target) {
    loadCategory(target.slug, target.title);
    loadSidebar(target.slug);
  }
}

// ─── Mobile Menu ──────────────────────────────────────────────────────────────

function toggleMenu() {
  const navbar = document.getElementById('navbar');
  if (navbar) navbar.classList.toggle('open');
}

// Close menu when clicking outside
document.addEventListener('click', e => {
  const navbar = document.getElementById('navbar');
  const menuIcon = document.querySelector('.menu-icon');
  if (
    window.innerWidth <= 815 &&
    navbar &&
    menuIcon &&
    !navbar.contains(e.target) &&
    !menuIcon.contains(e.target)
  ) {
    navbar.classList.remove('open');
  }
});

// ─── Sidebar Scroll Persistence ───────────────────────────────────────────────

function restoreSidebarScroll() {
  const sidebar = document.querySelector('#navbar ul');
  const scrollPos = sessionStorage.getItem('sidebar-scroll');
  if (scrollPos && sidebar) {
    sidebar.scrollTop = parseInt(scrollPos, 10);
  }
  if (sidebar) {
    sidebar.addEventListener('scroll', () => {
      sessionStorage.setItem('sidebar-scroll', sidebar.scrollTop);
    });
  }
}

// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Only run routing/markdown on the main index page (not about.html)
  const isMainPage = !!document.getElementById('page-content');

  if (isMainPage) {
    // Initial load
    handleRoute();

    // Handle browser back/forward & hash changes
    window.addEventListener('hashchange', handleRoute);
  }
  // Note: about.html calls loadSidebar(null) directly in its own <script> tag
});
