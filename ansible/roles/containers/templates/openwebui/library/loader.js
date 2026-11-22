// Open WebUI loads /static/loader.js on every page (an empty hook in the stock build). This one adds a "Library" row
// right below "Workspace" in the sidebar's user menu, linking to the files gallery at /library/. The row is a copy of
// the Workspace row, so it follows Open WebUI's styling; it is re-added whenever the menu is rendered again.
(() => {
  'use strict';
  const MARK = 'data-library-link';
  const ICON = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">' +
    '<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A1.5 1.5 0 0021.75 19.5V4.5A1.5 1.5 0 0020.25 3H3.75A1.5 1.5 0 002.25 4.5v15A1.5 1.5 0 003.75 21zM14.25 8.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"/></svg>';

  // The row to copy: the Workspace link's ancestor that sits in a vertical list. In the user menu that is the
  // .user-menu-row; for Workspace pinned to the sidebar the link sits inside horizontal flex wrappers, and adding
  // next to the link itself would put Library to its right.
  function rowOf(link) {
    let node = link.closest('.user-menu-row') || link;
    while (node.parentElement && node.parentElement !== document.body) {
      const style = getComputedStyle(node.parentElement);
      const horizontal = (style.display.includes('flex') && !style.flexDirection.startsWith('column')) || style.display.startsWith('inline');
      if (!horizontal || node.parentElement.querySelectorAll('a[href]').length > 1) break;
      node = node.parentElement;
    }
    return node;
  }

  function addLink(workspace) {
    const row = rowOf(workspace);
    if (row.nextElementSibling && row.nextElementSibling.hasAttribute(MARK)) return;
    const copy = row.cloneNode(true);
    copy.setAttribute(MARK, '');
    const link = copy.matches('a[href="/workspace"]') ? copy : copy.querySelector('a[href="/workspace"]');
    if (!link) return;
    // Drop what is not part of the link (pin buttons, tooltips) and anything that marks the current page.
    copy.querySelectorAll('button').forEach((button) => { if (!link.contains(button)) button.remove(); });
    copy.querySelectorAll('[aria-current]').forEach((node) => node.removeAttribute('aria-current'));
    link.setAttribute('href', '/library/');
    link.setAttribute('data-sveltekit-reload', '');
    link.removeAttribute('aria-current');
    const oldIcon = link.querySelector('svg');
    if (oldIcon) {
      const holder = document.createElement('span');
      holder.innerHTML = ICON;
      const icon = holder.firstChild;
      icon.setAttribute('class', oldIcon.getAttribute('class') || 'size-4');
      oldIcon.replaceWith(icon);
    }
    // The label: the innermost element whose text is Workspace's (translated) name.
    const name = (workspace.textContent || '').trim();
    const labels = [...link.querySelectorAll('*')].filter((node) => !node.closest('svg') && node.children.length === 0 && node.textContent.trim() === name && name);
    if (labels.length) labels.forEach((node) => { node.textContent = 'Library'; });
    else {
      const texts = [...link.querySelectorAll('div, span')].filter((node) => !node.closest('svg') && node.children.length === 0);
      if (texts.length) texts[texts.length - 1].textContent = 'Library';
    }
    link.title = 'Library';
    // A plain page load: /library/ is not one of Open WebUI's own routes.
    link.addEventListener('click', (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.button === 1) return;
      event.preventDefault(); event.stopPropagation();
      location.assign('/library/');
    }, true);
    row.after(copy);
  }

  function scan() {
    document.querySelectorAll('a[href="/workspace"]').forEach(addLink);
  }

  // Chats stream many DOM changes; look at most once per frame.
  let queued = false;
  const schedule = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; scan(); });
  };
  const start = () => {
    scan();
    new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true });
  };
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
})();
