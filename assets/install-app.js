// No automatic pop-up: installation is always initiated by the navigation button.
(() => {
  const button = document.getElementById('install-app');
  const dialog = document.getElementById('install-help');
  const instructions = document.getElementById('install-instructions');
  if (!button || !dialog || !instructions || !window.isSecureContext) return;
  const standalone = window.matchMedia('(display-mode: standalone)');
  let deferredPrompt = null;
  let installed = false;
  const isStandalone = () => installed || standalone.matches || navigator.standalone === true;
  const updateButton = () => { button.hidden = isStandalone(); };

  function showHelp() {
    const ios = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
      (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    instructions.textContent = ios
      ? 'No menu de compartilhamento do navegador, escolha “Adicionar à Tela de Início” e confirme em “Adicionar”. Se a opção não aparecer, abra este site no Safari.'
      : 'No menu do navegador, procure “Instalar aplicativo” ou “Adicionar à tela inicial”. No Safari do Mac, use Arquivo → Adicionar ao Dock. Se nenhuma dessas opções estiver disponível, tente abrir o site no Chrome ou Edge.';
    if (!dialog.open) dialog.showModal();
  }

  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    if (isStandalone()) return;
    deferredPrompt = event;
    updateButton();
  });
  window.addEventListener('appinstalled', () => {
    installed = true;
    deferredPrompt = null;
    if (dialog.open) dialog.close();
    updateButton();
  });
  standalone.addEventListener('change', updateButton);

  button.addEventListener('click', async () => {
    if (isStandalone()) return;
    if (!deferredPrompt) { showHelp(); return; }
    const prompt = deferredPrompt;
    deferredPrompt = null; // The browser event can be used only once.
    button.disabled = true;
    try {
      await prompt.prompt();
      const choice = await prompt.userChoice;
      if (choice.outcome === 'accepted') installed = true;
    } catch {
      showHelp();
    } finally {
      button.disabled = false;
      updateButton();
    }
  });
  updateButton();
})();
