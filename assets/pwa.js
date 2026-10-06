// Registration only: no custom installation UI and no beforeinstallprompt handler.
(() => {
  if (!window.isSecureContext || !('serviceWorker' in navigator)) return;
  const worker = new URL('../sw.js', document.currentScript.src);
  window.addEventListener('load', () => {
    navigator.serviceWorker.register(worker.href, {updateViaCache: 'none'}).catch(error => {
      console.warn('Não foi possível registrar o service worker do Clave Sol.', error);
    });
  }, {once: true});
})();
