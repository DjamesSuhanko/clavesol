"""Shared, progressively enhanced app installation controls."""
from html import escape


def install_head(base):
    base = escape(base, quote=True)
    return (f'<link rel="manifest" href="{base}/app.webmanifest">'
            f'<link rel="apple-touch-icon" href="{base}/assets/app-icon-192.png">'
            f'<script defer src="{base}/assets/install-app.js"></script>')


INSTALL_BUTTON = ('<button type="button" class="nav-install" id="install-app" '
                  'aria-haspopup="dialog" hidden>Instalar app</button>')

INSTALL_DIALOG = '''<dialog class="install-dialog" id="install-help" aria-labelledby="install-title" aria-describedby="install-instructions">
<h2 id="install-title">Instalar Clave Sol</h2>
<p id="install-instructions">No menu do navegador, procure “Instalar aplicativo” ou “Adicionar à tela inicial”. Se essa opção não estiver disponível, tente abrir o site no Chrome, Edge ou Safari.</p>
<form method="dialog"><button class="button" autofocus>Entendi</button></form>
</dialog>'''
