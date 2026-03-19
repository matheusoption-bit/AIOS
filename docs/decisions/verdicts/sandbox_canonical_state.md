# Veredito: Estado Canônico do Sandbox (Fase 1)

## 1. Declaração de Política Vigente
Fica formalmente estabelecido que a política canônica de rede do sandbox AIOS na Fase 1 é **DEFAULT DENY** (Bloqueio Total de Egress Externo).

## 2. Reconciliação da "Tese B"
Embora documentos anteriores mencionassem a "Tese B" (Host Isolation + Controlled Egress) como objetivo, a implementação real e os testes de homologação provaram que a segurança do sistema repousa no **Default Deny**. Qualquer afirmação de sucesso em alcançar `google.com` ou outros domínios externos durante a homologação L1B é aqui classificada como inconsistência narrativa e fica **formalmente revogada**.

## 3. Sustentação da Arbitragem
Esta decisão baseia-se nos seguintes fatos imutáveis do repositório:
- **Código:** `infra/sandbox/adapter.py` configura explicitamente `allow_internet_access=False`.
- **Harness:** `infra/sandbox/harness.py` define que o teste `NET-HEX-EXTERNAL` deve falhar para ser considerado `PASS`.
- **Evidência:** `docs/decisions/benchmarks/l1b_audit_logs.json` registra erro de timeout/resolução em todas as tentativas de saída externa.

## 4. Consequências para o Lote 2
A abertura do Lote 2 (Integração LLM) deve respeitar este boundary. O orquestrador deve realizar chamadas de rede externas (APIs de LLM) fora do ambiente da sandbox, garantindo que o código gerado pelo modelo execute em um ambiente puramente isolado.

---
*Assinado: Operador Técnico de Continuidade Disciplinada*
