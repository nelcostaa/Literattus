#!/bin/bash
# Script para configurar domínio personalizado no Route 53

set -euo pipefail

REGION="sa-east-1"
ALB_NAME="literattus-alb"
DOMAIN_NAME="${1:-}"

if [ -z "$DOMAIN_NAME" ]; then
    echo "Uso: $0 <dominio>"
    echo "Exemplo: $0 literattus.com"
    echo "Exemplo: $0 app.literattus.com"
    exit 1
fi

echo "🌐 Configurando domínio: $DOMAIN_NAME"

# Obter informações do ALB
echo "📡 Obtendo informações do ALB..."
ALB_ARN=$(aws elbv2 describe-load-balancers \
    --names "$ALB_NAME" \
    --region "$REGION" \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)

ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names "$ALB_NAME" \
    --region "$REGION" \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

ALB_ZONE_ID=$(aws elbv2 describe-load-balancers \
    --names "$ALB_NAME" \
    --region "$REGION" \
    --query 'LoadBalancers[0].CanonicalHostedZoneId' \
    --output text)

echo "✅ ALB DNS: $ALB_DNS"
echo "✅ ALB Zone ID: $ALB_ZONE_ID"

# Verificar se hosted zone existe
echo "🔍 Verificando hosted zone para $DOMAIN_NAME..."
ZONE_ID=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='${DOMAIN_NAME%.}.'].Id" \
    --output text | sed 's|/hostedzone/||')

if [ -z "$ZONE_ID" ]; then
    echo "⚠️  Hosted zone não encontrada para $DOMAIN_NAME"
    echo "📝 Criando hosted zone..."
    ZONE_ID=$(aws route53 create-hosted-zone \
        --name "$DOMAIN_NAME" \
        --caller-reference "literattus-$(date +%s)" \
        --region "$REGION" \
        --query 'HostedZone.Id' \
        --output text | sed 's|/hostedzone/||')
    echo "✅ Hosted zone criada: $ZONE_ID"
    
    # Mostrar nameservers
    echo ""
    echo "📋 IMPORTANTE: Configure os nameservers no seu registrador de domínio:"
    aws route53 get-hosted-zone \
        --id "$ZONE_ID" \
        --query 'DelegationSet.NameServers' \
        --output table
    echo ""
else
    echo "✅ Hosted zone encontrada: $ZONE_ID"
fi

# Criar/atualizar registro A (Alias)
echo "📝 Criando registro A (Alias) para $DOMAIN_NAME..."

CHANGE_BATCH=$(cat <<EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "$DOMAIN_NAME",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "$ALB_ZONE_ID",
        "DNSName": "$ALB_DNS",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
EOF
)

CHANGE_ID=$(aws route53 change-resource-record-sets \
    --hosted-zone-id "$ZONE_ID" \
    --change-batch "$CHANGE_BATCH" \
    --query 'ChangeInfo.Id' \
    --output text | sed 's|/change/||')

echo "✅ Registro A criado/atualizado!"
echo "🔄 Change ID: $CHANGE_ID"

# Verificar status da mudança
echo "⏳ Aguardando propagação DNS..."
aws route53 wait resource-record-sets-changed --id "$CHANGE_ID"

echo ""
echo "✅ Domínio configurado com sucesso!"
echo "🌐 Acesse: http://$DOMAIN_NAME"
echo ""
echo "📝 Próximos passos:"
echo "1. Aguarde 5-30 minutos para propagação DNS completa"
echo "2. Atualize ALLOWED_HOSTS no Django com: $DOMAIN_NAME"
echo "3. (Opcional) Configure HTTPS com certificado SSL"
echo ""
echo "Para atualizar ALLOWED_HOSTS, edite:"
echo "  - frontend/literattus_frontend/settings.py"
echo "  - Ou atualize a variável de ambiente na task definition ECS"

