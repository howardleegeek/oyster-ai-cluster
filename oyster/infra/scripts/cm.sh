#!/bin/bash
# ClawMarketing 常用操作

case "$1" in
  status)
    python3 ~/Downloads/dispatch/dispatch.py status clawmarketing
    ;;
  start)
    python3 ~/Downloads/dispatch/dispatch.py start clawmarketing
    ;;
  stop)
    python3 ~/Downloads/dispatch/dispatch.py stop clawmarketing
    ;;
  backend)
    ssh codex-node-1 "curl -s http://localhost:8000/"
    ;;
  frontend)
    curl -s https://frontend-alpha-gilt-61.vercel.app | head -5
    ;;
  deploy)
    cd ~/Downloads/clawmarketing/frontend && npx vercel --prod --yes --build-env NPM_CONFIG_LEGACY_PEER_DEPS=true
    ;;
  *)
    echo "用法: cm [status|start|stop|backend|frontend|deploy]"
    ;;
esac
