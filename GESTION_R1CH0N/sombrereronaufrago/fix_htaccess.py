import ftplib
import sys
import io

sys.path.insert(0, r'c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe')
from batallon.vault_soldier import VaultOrbe

v = VaultOrbe()

htaccess_content = (
    "Options -Indexes\n"
    "DirectoryIndex index.html\n"
    "\n"
    "<IfModule mod_rewrite.c>\n"
    "  RewriteEngine On\n"
    "  RewriteBase /\n"
    "</IfModule>\n"
    "\n"
    "# --- FORCE NO CACHE ---\n"
    "<IfModule mod_headers.c>\n"
    "  Header set Cache-Control \"no-cache, no-store, must-revalidate\"\n"
    "  Header set Pragma \"no-cache\"\n"
    "  Header set Expires 0\n"
    "</IfModule>\n"
    "\n"
    "<IfModule mod_expires.c>\n"
    "  ExpiresActive Off\n"
    "</IfModule>\n"
)

print("[*] Conectando a Hostinger...")
ftp = ftplib.FTP(v.recuperar('HOSTINGER_FTP_HOST'))
ftp.login(v.recuperar('HOSTINGER_FTP_USER'), v.recuperar('HOSTINGER_FTP_PASS'))
ftp.cwd('/public_html')

print("[*] Sobrescribiendo .htaccess...")
ftp.storbinary('STOR .htaccess', io.BytesIO(htaccess_content.encode('utf-8')))
print("[OK] .htaccess reparado. El sitio ahora sirve archivos estaticos.")

# Verificar que index.html esta subido
files = ftp.nlst()
print(f"[INFO] Archivos en public_html: {files}")
ftp.quit()
print("[OK] Listo! Refresca sombrereronaufrago.com en tu navegador.")
