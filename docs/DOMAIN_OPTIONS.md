# 🌐 Opções de Domínio para Literattus

Como você não tem um domínio ainda, aqui estão suas opções:

## ✅ Opção 1: Usar DNS do ALB (JÁ FUNCIONA - GRÁTIS)

**URL atual:**
```
http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com
```

✅ **Vantagens:**
- Já está funcionando
- Grátis
- Sem configuração adicional

❌ **Desvantagens:**
- URL longa e difícil de lembrar
- Não é profissional para produção

**Status:** ✅ **FUNCIONANDO AGORA**

---

## 💰 Opção 2: Registrar Domínio Novo

### 2.1 AWS Route 53 (Recomendado para AWS)

**Custo:** ~US$ 12-15/ano (.com) + US$ 0.50/mês para hosted zone

**Como registrar:**
1. Acesse: https://console.aws.amazon.com/route53/home#DomainListing:
2. Clique em "Register domain"
3. Busque o domínio desejado (ex: `literattus.com`)
4. Complete o registro

**Depois de registrar, execute:**
```bash
./scripts/setup-domain.sh literattus.com
```

### 2.2 Registro.br (Para .com.br)

**Custo:** ~R$ 40/ano

**Como registrar:**
1. Acesse: https://registro.br
2. Crie uma conta
3. Busque e registre o domínio (ex: `literattus.com.br`)
4. Configure DNS apontando para: `literattus-alb-96115082.sa-east-1.elb.amazonaws.com`

### 2.3 GoDaddy / Namecheap

**Custo:** ~US$ 10-15/ano

**Como registrar:**
1. Acesse GoDaddy.com ou Namecheap.com
2. Busque e registre o domínio
3. Configure DNS conforme `docs/DOMAIN_SETUP.md`

---

## 🆓 Opção 3: Domínios Temporários/Teste

### 3.1 Freenom (Gratuito - Limitado)

**Domínios:** .tk, .ml, .ga, .cf

**Como usar:**
1. Acesse: https://www.freenom.com
2. Registre um domínio gratuito
3. Configure DNS apontando para o ALB

⚠️ **Nota:** Domínios gratuitos podem ter limitações e não são recomendados para produção.

### 3.2 No-IP / DuckDNS (Dinâmicos)

Para testes locais apenas, não recomendado para ALB.

---

## 🎯 Recomendação

Para um projeto estudantil de 1 mês:

1. **Se for apenas para teste/apresentação:**
   - Use o DNS do ALB (já funciona!)
   - URL: `http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com`

2. **Se quiser algo mais profissional:**
   - Registre um domínio .com.br no Registro.br (~R$ 40/ano)
   - Ou um .com no Route 53 (~US$ 12/ano)
   - Configure DNS conforme `docs/DOMAIN_SETUP.md`

---

## 📋 Checklist para Configurar Domínio

Quando tiver um domínio:

- [ ] Domínio registrado
- [ ] DNS configurado apontando para ALB
- [ ] Aguardar propagação DNS (5-30 min)
- [ ] Atualizar ALLOWED_HOSTS no Django
- [ ] Testar acesso: `http://seu-dominio.com`
- [ ] (Opcional) Configurar HTTPS/SSL

---

## 🚀 Próximos Passos

**Se quiser continuar sem domínio:**
- ✅ Tudo já está funcionando!
- Acesse: `http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com`

**Se quiser registrar um domínio:**
1. Escolha um provedor (Route 53, Registro.br, etc.)
2. Registre o domínio
3. Execute: `./scripts/setup-domain.sh seu-dominio.com`
4. Aguarde propagação DNS
5. Acesse seu domínio!

