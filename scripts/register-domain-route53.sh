#!/bin/bash
# Script para verificar disponibilidade e registrar domínio no Route 53

set -euo pipefail

DOMAIN_NAME="${1:-}"

if [ -z "$DOMAIN_NAME" ]; then
    echo "Uso: $0 <dominio>"
    echo "Exemplo: $0 literattus.com"
    echo "Exemplo: $0 literattus.com.br"
    exit 1
fi

echo "🔍 Verificando disponibilidade do domínio: $DOMAIN_NAME"
echo ""

# Verificar disponibilidade
AVAILABILITY=$(aws route53domains check-domain-availability \
    --domain-name "$DOMAIN_NAME" \
    --region us-east-1 \
    --query 'Availability' \
    --output text 2>/dev/null || echo "ERROR")

if [ "$AVAILABILITY" = "ERROR" ]; then
    echo "⚠️  Erro ao verificar disponibilidade. Verificando se você tem permissões..."
    echo ""
    echo "Para registrar domínio no Route 53, você precisa:"
    echo "1. Acessar AWS Console → Route 53 → Registered domains"
    echo "2. Clicar em 'Register domain'"
    echo "3. Buscar e registrar o domínio desejado"
    echo ""
    echo "Ou use um provedor externo como:"
    echo "- Registro.br (para .com.br): https://registro.br"
    echo "- GoDaddy: https://www.godaddy.com"
    echo "- Namecheap: https://www.namecheap.com"
    exit 1
fi

case "$AVAILABILITY" in
    "AVAILABLE")
        echo "✅ Domínio $DOMAIN_NAME está DISPONÍVEL!"
        echo ""
        echo "Para registrar:"
        echo "1. Acesse: https://console.aws.amazon.com/route53/home#DomainListing:"
        echo "2. Clique em 'Register domain'"
        echo "3. Busque por: $DOMAIN_NAME"
        echo "4. Complete o registro (custo: ~US$ 12-15/ano para .com)"
        ;;
    "UNAVAILABLE")
        echo "❌ Domínio $DOMAIN_NAME NÃO está disponível"
        ;;
    "RESERVED")
        echo "⚠️  Domínio $DOMAIN_NAME está RESERVADO"
        ;;
    "PREMIUM")
        echo "💰 Domínio $DOMAIN_NAME é PREMIUM (custo adicional)"
        ;;
    *)
        echo "❓ Status desconhecido: $AVAILABILITY"
        ;;
esac

