/* Progressive enhancement: navigation and content remain usable without JavaScript. */
(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-nav');
  const compact = window.matchMedia('(max-width: 1000px)');
  const setOpen = (open) => {
    nav.hidden = compact.matches && !open;
    toggle.setAttribute('aria-expanded', String(!nav.hidden));
  };
  setOpen(false);
  toggle.addEventListener('click', () => setOpen(nav.hidden));
  compact.addEventListener('change', () => setOpen(false));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && compact.matches && !nav.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });
  const base = new URL(document.querySelector('header .brand').href).pathname;
  const path = location.pathname.slice(base.length).split('/')[0];
  for (const link of nav.querySelectorAll('a')) {
    if (new URL(link.href).pathname.slice(base.length).split('/')[0] === path) {
      link.setAttribute('aria-current', 'page');
    }
  }
  const top = document.querySelector('.back-top');
  const update = () => { top.hidden = window.scrollY < 650; };
  window.addEventListener('scroll', update, { passive:true });
  update();
  top.addEventListener('click', () => {
    window.scrollTo({ top:0, behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    document.querySelector('header .brand').focus({ preventScroll:true });
  });
})();
