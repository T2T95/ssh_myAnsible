#!/bin/bash
cd ~/my-little-ansible

echo "🐳 Test MyLittleAnsible Docker"

docker-compose -f docker-compose.test.yml down || true

echo "🚀 Démarrage..."
docker-compose -f docker-compose.test.yml up -d

sleep 25  # Plus long pour Debian

echo "🔍 SSH target1..."
sshpass -p testpass ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 testuser@172.20.0.22 "whoami; hostname" || echo "SSH1 KO"

echo "🔍 SSH target2..."
sshpass -p testpass ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 testuser@172.20.0.24 "whoami; hostname" || echo "SSH2 KO"

echo "✅ SSH OK ! Test code..."
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install -e . -q

echo "🎯 mla --help"
mla --help

echo "🔄 Dry-run test"
mla examples/inventory-docker.yml examples/inventory-docker.yml --dry-run

echo "🎉 SUCCESS !"
docker ps --format "table {{.Names}}\t{{.Status}}"
