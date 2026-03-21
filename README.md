<div align="center">

# 🤖 AIOS

**Autonomous Intelligent Operating System**

_Um sistema de execução autônoma de intents com auditoria criptográfica, sandbox isolada e rollback automático._

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![E2B](https://img.shields.io/badge/Sandbox-E2B-FF6B35?style=for-the-badge)](https://e2b.dev)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 📖 O que é o AIOS?

O **AIOS** (Autonomous Intelligent Operating System) é uma plataforma experimental de execução autônoma de intents com três pilares fundamentais:

| Pilar | Descrição |
|---|---|
| 🔐 **Auditoria Criptográfica** | Ledger imutável com hash chain SHA-256 — cada evento referencia o anterior |
| 📦 **Sandbox Isolada** | Execução via [E2B](https://e2b.dev) — código roda em ambiente completamente isolado do host |
| 🔄 **Rollback Automático** | Falha de verificação, timeout ou violação de segurança acionam rollback via Git |

---

## 🏗️ Arquitetura

```
Intent → FSM Orquestrador → Sandbox E2B → Verificação → Ledger
              │                                │
              ├─ Policy Guard                  ├─ SUCCESS → commit
              ├─ Path Policy                   └─ FAILURE → rollback
              └─ Hash Chain Ledger
```

### Máquina de Estados (FSM)

```
IDLE
  └─→ INTENT_VALIDATION
        ├─→ FAILURE (proposta inválida / budget exceeded)
        └─→ SNAPSHOT_PENDING
              └─→ EXECUTION_PENDING
                    ├─→ ERROR (violação de segurança)
                    ├─→ FAILURE + ROLLBACK (timeout)
                    └─→ VERIFICATION_PENDING
                          ├─→ FAILURE + ROLLBACK (verificação falhou)
                          └─→ SUCCESS (commit do novo git_ref)
```

### Módulos

```
src/
├── common/
│   └── prompt_context.py     # Contexto compartilhado para prompts LLM
├── lote2/                    # Núcleo de execução — Fase 2
│   ├── lote2_runner.py       # Orquestrador principal
│   ├── ledger.py             # Ledger com hash chain SHA-256
│   ├── provider_client.py    # Cliente OpenAI
│   ├── response_schema.py    # Schemas Pydantic de resposta
│   └── validate_ledger.py    # Validador de integridade do ledger
└── lote3/                    # Núcleo de segurança — Fase 3
    ├── lote3_runner.py       # Orquestrador com policy enforcement
    ├── path_policy.py        # Políticas de acesso a caminhos
    ├── policy_guard.py       # Guard que valida intents contra políticas
    ├── provider_client.py    # Cliente OpenAI com retry
    └── response_schema.py    # Schemas de resposta com validação
```

---

## ⚡ Início Rápido

### Pré-requisitos

- Python 3.11+
- Conta [OpenAI](https://platform.openai.com/api-keys) (GPT-4)
- Conta [E2B](https://e2b.dev/docs/getting-started/api-key) (sandbox)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/matheusoption-bit/AIOS.git
cd AIOS

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt
```

### Configuração

```bash
# Copie o template de variáveis de ambiente
cp example.env .env

# Edite .env com suas credenciais
nano .env
```

```dotenv
# .env
OPENAI_API_KEY=sk-...         # Obtenha em: https://platform.openai.com/api-keys
E2B_API_KEY=e2b_...           # Obtenha em: https://e2b.dev/docs/getting-started/api-key
```

---

## 🧪 Benchmark — 5 Cenários

O `benchmark_runner.py` executa uma bateria de 5 cenários que cobrem todos os caminhos do FSM:

```bash
python benchmark_runner.py
```

| Cenário | Intent | Comportamento | Resultado Esperado |
|---|---|---|---|
| **S1** | `PATCH` | Caminho feliz | `SUCCESS` + novo git_ref |
| **S2** | `UNKNOWN` | Proposta malformed | `FAILURE: MALFORMED_PROPOSAL` |
| **S3** | `SHELL rm -rf /` | Verificação falha | `FAILURE: VERIFICATION_FAILED` + rollback |
| **S4** | `PATCH large` | Timeout com efeito material | `FAILURE: TIMEOUT` + rollback |
| **S5** | `SHELL eval` | Violação de segurança | `ERROR: SECURITY_VIOLATION` + rollback |

Ao final, o benchmark valida a **integridade da hash chain** do ledger:

```
--- Verificação de Integridade do Ledger ---
Sucesso: Hash Chain de 256 bits 100% íntegra.
Ledger final persistido com N entradas.
```

---

## 🔐 Ledger Criptográfico

Cada evento registrado no sistema gera uma entrada no ledger com:

```python
{
  "index": 0,
  "event_type": "INTENT_PROPOSED",
  "intent_id": "uuid-v4",
  "timestamp": "2026-03-21T00:00:00Z",
  "payload": { ... },
  "prev_hash": "0000...0000",  # Hash da entrada anterior
  "git_ref": "base-commit-000",
  "entry_hash": "sha256(...)"  # SHA-256 desta entrada
}
```

A integridade da cadeia é verificada comparando `ledger[i].prev_hash === ledger[i-1].entry_hash` para toda a série.

---

## 🛡️ Segurança

O AIOS implementa múltiplas camadas de defesa:

1. **Policy Guard** — Valida se o intent respeita as políticas definidas antes da execução
2. **Path Policy** — Define quais caminhos do filesystem o agente pode ler/escrever
3. **Sandbox E2B** — Execução completamente isolada do host (sem acesso ao sistema real)
4. **Rollback Automático** — Qualquer falha com efeito material dispara `git reset --hard`
5. **Auditoria Imutável** — O ledger com hash chain garante rastreabilidade completa

---

## 🧩 Dependências

| Pacote | Versão | Uso |
|---|---|---|
| `pydantic` | `>=2,<3` | Validação de schemas e contratos de dados |
| `python-dotenv` | `>=1,<2` | Carregamento de variáveis de ambiente |
| `e2b` | `>=2,<3` | Sandbox isolada para execução de código |
| `openai` | `>=1,<2` | Motor de decisão LLM (GPT-4) |

---

## 📂 Estrutura do Projeto

```
AIOS/
├── src/
│   ├── common/             # Utilitários compartilhados
│   ├── lote2/              # Fase 2: execução + ledger
│   └── lote3/              # Fase 3: segurança + policy enforcement
├── artifacts/              # Artefatos gerados pelas execuções
├── docs/                   # Documentação técnica detalhada
├── infra/                  # Configurações de infraestrutura
├── scripts/                # Scripts de utilidade
├── tests/                  # Testes automatizados
├── benchmark_runner.py     # Runner de benchmark FSM (5 cenários)
├── example.env             # Template de variáveis de ambiente
└── requirements.txt        # Dependências Python
```

---

## 🗺️ Roadmap

- [ ] Interface CLI interativa para submissão de intents
- [ ] Dashboard de monitoramento do ledger em tempo real
- [ ] Suporte a múltiplos providers LLM (Anthropic, Gemini)
- [ ] API REST para integração com outros sistemas
- [ ] Integração nativa com ORACLE-OS para auto-evolução

---

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do repositório
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit suas mudanças: `git commit -m 'feat: adicionar minha feature'`
4. Push para a branch: `git push origin feature/minha-feature`
5. Abra um Pull Request
