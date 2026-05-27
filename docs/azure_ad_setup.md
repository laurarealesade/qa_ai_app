# Azure AD — Ya no es necesario

La solución fue rediseñada para no requerir Azure AD ni permisos de administrador.

El flujo ahora usa:
- **Regla de Outlook** → guarda los adjuntos automáticamente en una carpeta de OneDrive
- **Python** → lee esa carpeta local sincronizada por OneDrive
- **No se necesita** registrar ninguna app ni esperar aprobación de IT

Ver la guía completa en `docs/outlook_rule_setup.md`.
