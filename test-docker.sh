#!/bin/bash
cd ~/my-little-ansible

echo "🐳 Test MyLittleAnsible Docker"

docker-compose -f docker-compose.test.yml down || true

echo "🚀 Démarrage..."
docker-compose -f docker-compose.test.yml up -d

sleep 20

echo "🔍 SSH target1..."
sshpass -p testpass ssh -o StrictHostKeyChecking=no testuser@172.20.0.22 whoami || echo "SSH1 KO"

echo "🔍 SSH target2..."
sshpass -p testpass ssh -o StrictHostKeyChecking=no testuser@172.20.0.24 whoami || echo "SSH2 KO"

echo "✅ SSH tests OK ! Installation Python..."
python3 -m venv venv --clear
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo "🎯 Test MLA..."
mla --help
echo "🔄 Test dry-run..."
mla -f examples/inventory-docker.yml examples/inventory-docker.yml --dry-run

echo "🎉 FINI !"
docker ps
