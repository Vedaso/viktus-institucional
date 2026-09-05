<context>
## Projeto: Viktus Web Presence — Fase 4: Meta Business Verification

**Esta fase é operacional, não técnica.** Não há código a escrever.
O objetivo é guiar a submissão de `viktus.com.br` para verificação do Meta Business Manager,
desbloqueando o uso do WhatsApp Business API no nível do Grupo Viktus.

### Pré-requisito obrigatório
A Fase 3 deve estar concluída: `viktus.com.br` deve estar no ar com o site institucional,
incluindo as páginas `/privacidade` e `/termos` com conteúdo real (não placeholder).

### Contexto
O Worker `viktus-care-landing` já serve `/care/privacidade` e `/care/termos` para o produto Care.
O site institucional serve `/privacidade` e `/termos` para o Grupo Viktus.
São documentos separados — a verificação Meta usa o domínio raiz `viktus.com.br`.

### ⚠️ RESTRIÇÃO CRÍTICA
**NUNCA** disparar as chamadas de API Meta (`request_code`, `verify_code`, `register`, ou equivalentes
no Graph API) sem confirmação EXPLÍCITA do Victor. Esta fase produz apenas um guia e checklist.
Toda ação na plataforma Meta deve ser executada manualmente pelo Victor.

### Dados disponíveis
- Domínio: `viktus.com.br`
- Conta Cloudflare: `victor_omena@hotmail.com`
- Email Meta existente: verificar com Victor antes de usar
</context>

<task>
Produzir um guia passo a passo salvo em
`~/OneDrive/Documentos/Claude/dev/viktus-institucional/guia-meta-verification.md`.

### 1. Checklist do site antes de submeter

Verificar que estas páginas existem e têm conteúdo adequado para a Meta:

```bash
curl -sI https://viktus.com.br/ | grep "^HTTP"
# Deve retornar 200 — página inicial com nome da empresa

curl -sI https://viktus.com.br/sobre | grep "^HTTP"
# Deve retornar 200 — deve ter CNPJ, endereço, razão social

curl -sI https://viktus.com.br/privacidade | grep "^HTTP"
# Deve retornar 200 — política de privacidade com dados de contato do DPO

curl -sI https://viktus.com.br/termos | grep "^HTTP"
# Deve retornar 200 — termos de uso

curl -sI https://viktus.com.br/contato | grep "^HTTP"
# Deve retornar 200 — canal de contato disponível
```

O guia deve incluir o checklist de conteúdo que a Meta exige:
- [ ] Nome legal da empresa (razão social)
- [ ] CNPJ visível no site
- [ ] Endereço físico ou virtual válido
- [ ] Descrição dos produtos/serviços
- [ ] Política de Privacidade com: quais dados coleta, finalidade, como exercer direitos LGPD
- [ ] Termos de Uso
- [ ] Canal de contato público (email, formulário ou telefone)
- [ ] Sem conteúdo proibido pela Meta (drogas, armas, conteúdo adulto, etc.)

### 2. Passos no Meta Business Manager

Documentar a sequência exata de ações que Victor deve executar:

1. Acessar `business.facebook.com`
2. Selecionar ou criar o Business Manager para Viktus
3. Ir em **Configurações → Informações do negócio**
4. Verificar que o domínio `viktus.com.br` está adicionado
5. Ir em **Brand Safety → Domínios** → Adicionar `viktus.com.br` se não estiver
6. Clicar em **Verificar domínio** e escolher o método:
   - **Recomendado: Meta-tag** (adicionar `<meta name="facebook-domain-verification" content="...">` no `<head>` do site)
   - Alternativa: arquivo TXT DNS
   - Alternativa: arquivo HTML no servidor
7. Se Meta-tag: anotar o código gerado, voltar ao repo `viktus-institucional` e adicionar ao layout base
8. Após adicionar a meta-tag e fazer deploy, voltar ao Business Manager e clicar em **Verificar**

Para verificação do negócio (além do domínio):
1. Ir em **Configurações → Verificação do negócio**
2. Selecionar tipo: **Empresa** (não Criador)
3. Submeter: CNPJ, documento oficial (contrato social ou certidão), comprovante de telefone ou email corporativo
4. Aguardar análise (1-5 dias úteis)

### 3. Integração WhatsApp Business API (após verificação)

Após a verificação ser aprovada, documentar os próximos passos para:
- Criar o App no Meta for Developers
- Ativar o produto WhatsApp Business
- Configurar o número de telefone
- **NÃO executar nenhuma dessas ações — apenas documentar o passo a passo**

### 4. Checklist de documentos a preparar

Victor deve ter em mãos antes de submeter:
- [ ] CNPJ ativo (consultar na Receita Federal se necessário)
- [ ] Contrato social ou documento de abertura da empresa
- [ ] Comprovante de endereço da empresa (conta de água/luz/telefone ou contrato de aluguel)
- [ ] Número de telefone que será usado no WhatsApp Business
- [ ] Email corporativo (não Gmail/Hotmail — preferir @viktus.com.br ou @vedaso.com)

### 5. Possíveis problemas e soluções

Documentar os cenários mais comuns de rejeição Meta e como resolver:
- Site incompleto (faltou CNPJ, endereço) → adicionar à página `/sobre`
- Domínio não verificado → refazer verificação com meta-tag
- CNPJ inválido ou empresa muito nova → aguardar e tentar novamente
- Conteúdo inconsistente entre site e documentos submetidos → corrigir site antes de re-submeter
</task>

<constraints>
- **NUNCA** disparar chamadas à API Meta (`request_code`, `verify_code`, `register`) sem confirmação explícita do Victor.
- Este guia é apenas documentação — nenhuma ação deve ser executada automaticamente.
- Não criar App na Meta, não configurar WhatsApp número, não submeter formulário — apenas documentar.
- Se precisar adicionar a meta-tag de verificação ao site, criar um PR no repo `viktus-institucional` e aguardar aprovação do Victor antes de fazer deploy.
- CNPJ e dados pessoais da empresa não devem ser incluídos diretamente neste guia — deixar placeholders para Victor preencher.
</constraints>

<criterios-de-aceite>
- [ ] Arquivo `guia-meta-verification.md` criado com todos os passos documentados
- [ ] Checklist de conteúdo do site preenchido com status atual
- [ ] Checklist de documentos necessários listado
- [ ] Sequência de ações no Business Manager documentada com capturas de tela dos menus (ou descrição textual precisa)
- [ ] Seção de troubleshooting com os 4-5 problemas mais comuns
- [ ] Nenhuma ação foi disparada na plataforma Meta
</criterios-de-aceite>
