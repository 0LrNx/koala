#!/bin/bash
case "$1" in
    start)
        echo "🚀 Démarrage du bot..."
        sudo systemctl start koala-bot
        ;;
    stop)
        echo "🛑 Arrêt du bot..."
        sudo systemctl stop koala-bot
        ;;
    restart)
        echo "🔄 Redémarrage du bot..."
        sudo systemctl restart koala-bot
        ;;
    status)
        echo "📊 Status du bot:"
        sudo systemctl status koala-bot
        ;;
    logs)
        echo "📋 Logs du bot (Ctrl+C pour quitter):"
        sudo journalctl -u koala-bot -f
        ;;
    update)
        echo "📥 Mise à jour manuelle..."
        cd ~/koala-bot
        git pull
        source .venv/bin/activate
        pip install -r requirements.txt
        sudo systemctl restart koala-bot
        echo "✅ Mise à jour terminée"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|update}"
        echo ""
        echo "Commandes disponibles:"
        echo "  start   - Démarrer le bot"
        echo "  stop    - Arrêter le bot"
        echo "  restart - Redémarrer le bot"
        echo "  status  - Voir le status"
        echo "  logs    - Voir les logs en temps réel"
        echo "  update  - Mettre à jour manuellement"
        exit 1
        ;;
esac
