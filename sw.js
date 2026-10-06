// Leave installation promotion entirely to the browser. Do not cache article
// pages: the site's existing versioned URLs remain responsible for updates.
const offlinePage = `<!doctype html>
<html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Clave Sol — sem conexão</title>
<style>body{margin:0;padding:40px 24px;background:#f7f6f0;color:#173b34;font:18px/1.6 system-ui,sans-serif}main{max-width:560px;margin:10vh auto}h1{font-size:32px}</style>
<main><h1>Você está sem conexão</h1><p>O Clave Sol precisa de internet para abrir esta página. Verifique a conexão e recarregue para continuar.</p></main></html>`;

self.addEventListener('install', event => {
  event.waitUntil(self.skipWaiting());
});
self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || event.request.mode !== 'navigate' ||
      new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(fetch(event.request).catch(() => new Response(offlinePage, {
    headers: {'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store'}
  })));
});
