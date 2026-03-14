#!/bin/bash
# Script de ayuda para configurar DuckDNS

echo "🦆 Guía rápida para configurar DuckDNS con Ollama Hardened"
echo "======================================================="
echo "1. Ve a https://www.duckdns.org/ y haz login (con Google, GitHub, etc)."
echo "2. En la caja 'sub domain', escribe un nombre único (ej. mi-ia-privada)."
echo "3. Haz clic en 'add domain'."
echo "4. Asegúrate de que la 'current ip' que aparece junto a tu nuevo dominio sea: 31.220.80.78"
echo "   (Si no lo es, haz clic en el botón 'update ip' y pon 31.220.80.78 manualmente)."
echo "======================================================="
echo ""
echo "Una vez que hayas completado esos pasos en la web de DuckDNS:"
read -p "Introduce el subdominio completo que has creado (ejemplo: mi-ia-privada.duckdns.org): " DUCK_DOMAIN

if [ -z "$DUCK_DOMAIN" ]; then
    echo "❌ Operación cancelada. No se ha introducido un dominio."
    exit 1
fi

echo "======================================================="
echo "🔄 Actualizando configuración a $DUCK_DOMAIN ..."

# Reemplazar el dominio en el .env
sed -i "s/^DOMAIN=.*/DOMAIN=$DUCK_DOMAIN/" .env
sed -i "s/^OLLAMA_ORIGINS=.*/OLLAMA_ORIGINS=https:\/\/$DUCK_DOMAIN/" .env

echo "✅ Archivo .env actualizado."

# Eliminar 'tls internal' de Caddyfile para que pida un certificado real a Let's Encrypt
sed -i '/tls internal/d' Caddyfile
echo "✅ Caddyfile actualizado (Let's Encrypt activado)."

echo "🚀 Aplicando cambios y solicitando certificado SSL real..."
# Usamos el script de actualización que ya tenemos
echo "n" | ./update.py

echo "======================================================="
echo "🎉 ¡Todo listo! Tu FQDN es: https://$DUCK_DOMAIN"
echo "⚠️ Nota: Let's Encrypt puede tardar entre 30 segundos y 2 minutos en emitir el certificado la primera vez."
