# 🌐 Configuração de Domínio Personalizado para Literattus

Este guia explica como configurar um domínio personalizado (ex: `literattus.com` ou `app.literattus.com`) para o ALB.

## 📋 Pré-requisitos

1. **Domínio registrado** em um provedor DNS (Route 53, GoDaddy, Namecheap, etc.)
2. **Acesso ao painel DNS** do seu provedor de domínio

## 🎯 Opção 1: Usando AWS Route 53 (Recomendado)

### Passo 1: Registrar/Criar Hosted Zone no Route 53

```bash
# Criar hosted zone para seu domínio
aws route53 create-hosted-zone \
  --name literattus.com \
  --caller-reference $(date +%s) \
  --region sa-east-1
```

### Passo 2: Obter informações do ALB

```bash
# Obter DNS name e Hosted Zone ID do ALB
aws elbv2 describe-load-balancers \
  --names literattus-alb \
  --region sa-east-1 \
  --query 'LoadBalancers[0].{DNSName:DNSName,CanonicalHostedZoneId:CanonicalHostedZoneId}'
```

### Passo 3: Criar registro A (Alias) no Route 53

```bash
# Substitua ZONE_ID, DOMAIN e ALB_DNS_NAME pelos valores corretos
aws route53 change-resource-record-sets \
  --hosted-zone-id ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "literattus.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "ALB_HOSTED_ZONE_ID",
          "DNSName": "literattus-alb-96115082.sa-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

**Para subdomínio (ex: app.literattus.com):**
```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.literattus.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "ALB_HOSTED_ZONE_ID",
          "DNSName": "literattus-alb-96115082.sa-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

## 🌍 Opção 2: Usando Provedor DNS Externo (GoDaddy, Namecheap, etc.)

### Passo 1: Obter informações do ALB

**DNS Name do ALB:**
```
literattus-alb-96115082.sa-east-1.elb.amazonaws.com
```

**Hosted Zone ID do ALB (para Route 53 Alias):**
```
Z2P70J7EXAMPLE (obtenha via AWS CLI)
```

### Passo 2: Configurar no painel DNS do seu provedor

#### Para GoDaddy:
1. Acesse: https://www.godaddy.com → Meus Produtos → DNS
2. Adicione um novo registro:
   - **Tipo:** A
   - **Nome:** @ (para domínio raiz) ou `app` (para subdomínio)
   - **Valor:** `literattus-alb-96115082.sa-east-1.elb.amazonaws.com`
   - **TTL:** 600 segundos

#### Para Namecheap:
1. Acesse: https://www.namecheap.com → Domain List → Manage → Advanced DNS
2. Adicione um novo registro:
   - **Type:** A Record
   - **Host:** @ (para domínio raiz) ou `app` (para subdomínio)
   - **Value:** `literattus-alb-96115082.sa-east-1.elb.amazonaws.com`
   - **TTL:** Automatic

#### Para Cloudflare:
1. Acesse: https://dash.cloudflare.com → Selecione seu domínio → DNS
2. Adicione um novo registro:
   - **Type:** CNAME
   - **Name:** @ (para domínio raiz) ou `app` (para subdomínio)
   - **Target:** `literattus-alb-96115082.sa-east-1.elb.amazonaws.com`
   - **Proxy status:** DNS only (desabilitar proxy para ALB)

**⚠️ Nota:** Alguns provedores DNS não permitem CNAME no domínio raiz (@). Nesse caso, use um subdomínio como `app.literattus.com` ou `www.literattus.com`.

## 🔒 Opção 3: Adicionar HTTPS com Certificado SSL (Opcional mas Recomendado)

### Passo 1: Solicitar certificado no AWS Certificate Manager (ACM)

```bash
# Solicitar certificado público
aws acm request-certificate \
  --domain-name literattus.com \
  --subject-alternative-names "*.literattus.com" \
  --validation-method DNS \
  --region sa-east-1
```

### Passo 2: Validar o certificado

1. Obtenha os registros DNS de validação:
```bash
aws acm describe-certificate \
  --certificate-arn CERTIFICATE_ARN \
  --region sa-east-1 \
  --query 'Certificate.DomainValidationOptions'
```

2. Adicione os registros CNAME no seu DNS conforme retornado acima

### Passo 3: Criar listener HTTPS no ALB

```bash
# Obter ARN do certificado após validação
CERT_ARN="arn:aws:acm:sa-east-1:147054060547:certificate/xxxxx"

# Criar listener HTTPS
aws elbv2 create-listener \
  --load-balancer-arn $(aws elbv2 describe-load-balancers --names literattus-alb --region sa-east-1 --query 'LoadBalancers[0].LoadBalancerArn' --output text) \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$(aws elbv2 describe-target-groups --names literattus-frontend-tg --region sa-east-1 --query 'TargetGroups[0].TargetGroupArn' --output text) \
  --region sa-east-1
```

### Passo 4: Adicionar regra de roteamento para /api/* no listener HTTPS

```bash
# Obter listener ARN
LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $(aws elbv2 describe-load-balancers --names literattus-alb --region sa-east-1 --query 'LoadBalancers[0].LoadBalancerArn' --output text) \
  --region sa-east-1 \
  --query 'Listeners[?Port==`443`].ListenerArn' --output text)

# Adicionar regra para /api/*
aws elbv2 create-rule \
  --listener-arn $LISTENER_ARN \
  --priority 10 \
  --conditions Field=path-pattern,Values='/api/*' \
  --actions Type=forward,TargetGroupArn=$(aws elbv2 describe-target-groups --names literattus-backend-tg --region sa-east-1 --query 'TargetGroups[0].TargetGroupArn' --output text) \
  --region sa-east-1
```

### Passo 5: Atualizar configurações do Django

Após configurar HTTPS, atualize `frontend/literattus_frontend/settings.py`:

```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Reativar redirect para HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

## 📝 Atualizar ALLOWED_HOSTS

Após configurar o domínio, atualize `ALLOWED_HOSTS` no Django:

```python
ALLOWED_HOSTS = [
    'literattus.com',
    'www.literattus.com',
    'app.literattus.com',
    '*.elb.amazonaws.com',  # Manter para ALB
    '*',  # Ou remover em produção
]
```

Ou via variável de ambiente na task definition:
```json
{
  "name": "ALLOWED_HOSTS",
  "value": "literattus.com,www.literattus.com,app.literattus.com"
}
```

## ✅ Verificação

Após configurar o DNS, aguarde a propagação (pode levar até 48 horas, geralmente 5-30 minutos):

```bash
# Verificar DNS
dig literattus.com
nslookup literattus.com

# Testar acesso
curl -I http://literattus.com
```

## 🎯 Resumo Rápido

1. **Registre/Configure domínio** no seu provedor DNS
2. **Aponte DNS** para: `literattus-alb-96115082.sa-east-1.elb.amazonaws.com`
3. **Aguarde propagação** DNS (5-30 minutos)
4. **Atualize ALLOWED_HOSTS** no Django
5. **Opcional:** Configure HTTPS com certificado SSL

## 📚 Referências

- [AWS Route 53 Documentation](https://docs.aws.amazon.com/route53/)
- [AWS Certificate Manager](https://docs.aws.amazon.com/acm/)
- [ALB Listener Configuration](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html)

