# Especificação Operacional: Lote 2 Mínimo (Integração LLM)

## 1. Objetivo
Provar a integração funcional básica entre o Runtime do AIOS, um provedor de LLM e a Sandbox, garantindo a execução de comandos estruturados em ambiente isolado e o registro íntegro no Ledger.

## 2. Escopo do Recorte Mínimo
Este lote foca na execução linear de uma intenção simples, sem loops ou múltiplos agentes.

- **Provedor:** OpenAI (GPT-4o) ou Anthropic (Claude 3.5 Sonnet).
- **Tipo de Intent:** `SHELL` (Execução de comando único).
- **Fluxo:** One-shot (Insumo -> Comando -> Execução -> Fim).

## 3. Fluxo Canônico de Execução
1. **Entrada:** Recebimento de uma `Intent` (ex: "Crie um arquivo de teste").
2. **Prompts:** Geração de prompt pelo Orquestrador enviada ao LLM (fora da sandbox).
3. **Saída LLM:** Resposta obrigatoriamente em JSON estruturado.
4. **Validação:** Orquestrador valida o schema da resposta.
5. **Execução:** Comando extraído é enviado ao `E2BSandboxAdapter`.
6. **Ledger:** Registro do prompt, da resposta bruta e do resultado da sandbox.
7. **Encerramento:** Retorno do status final ao usuário.

## 4. Contrato de Saída do LLM (JSON)
O modelo deve responder estritamente neste formato:
```json
{
  "command": "string",
  "explanation": "string (opcional)"
}
```
- **Políticas de Falha:**
  - JSON inválido -> Estado `FAILURE` (Reason: `MALFORMED_LLM_RESPONSE`).
  - Campo `command` ausente -> Estado `FAILURE` (Reason: `INVALID_ACTION`).

## 5. Modos de Falha Monitorados
- **Timeout Provider:** Erro na chamada de API externa.
- **Timeout Sandbox:** Comando excedeu o tempo limite na VM.
- **Segurança:** Bloqueio de rede na sandbox deve permanecer ativo (Default Deny).
- **Integridade:** Qualquer falha de escrita no Ledger interrompe a cadeia.

## 6. Critérios de Aceitação (Definition of Done)
- [ ] Chamada ao LLM registrada no Ledger como `RAW_LLM_RESPONSE`.
- [ ] Comando executado com sucesso dentro da sandbox provado via `read_file`.
- [ ] Hash Chain do Ledger 100% íntegra após a execução.
- [ ] Zero dependência de rede interna da sandbox para a chamada do LLM.

## 7. Exclusões Explícitas (Não entra no Lote 2)
- Múltiplos agentes ou diálogos entre modelos.
- Memória persistente entre sessões (Stateful context).
- Auto-correção (Reflection loops).
- Interface Gráfica ou Dashboard.

---
*Status: ABERTO PARA IMPLEMENTAÇÃO*
