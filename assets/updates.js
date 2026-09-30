// Check on entry and when returning to a tab, never interrupt music or reading.
const script = document.currentScript;
const currentVersion = script.dataset.version;
const manifest = new URL(script.dataset.manifest, location.href);
let checking = false;
let lastCheck = 0;
let notice;
async function checkForUpdate() {
  if (document.hidden || checking || notice || Date.now() - lastCheck < 60000) return;
  checking = true;
  lastCheck = Date.now();
  try {
    const url = new URL(manifest);
    url.searchParams.set('check', String(Date.now()));
    const response = await fetch(url, {cache: 'no-store'});
    if (!response.ok) return;
    const {version} = await response.json();
    if (!/^[a-f0-9]{20}$/.test(version) || version === currentVersion) return;
    notice = document.createElement('div');
    notice.className = 'update-notice';
    notice.setAttribute('role', 'status');
    const message = document.createElement('span');
    message.textContent = 'Uma nova versão do Clave Sol está disponível.';
    const link = document.createElement('a');
    link.textContent = 'Atualizar';
    const destination = new URL(location.href);
    destination.searchParams.set('_cs', version);
    link.href = destination.href;
    const dismiss = document.createElement('button');
    dismiss.type = 'button';
    dismiss.textContent = 'Depois';
    dismiss.addEventListener('click', () => notice.remove());
    notice.append(message, link, dismiss);
    document.body.append(notice);
  } catch {
    // Offline or unavailable endpoint: keep the current page usable.
  } finally {
    checking = false;
  }
}
checkForUpdate();
document.addEventListener('visibilitychange', checkForUpdate);
