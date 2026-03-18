# Plano de Validação Empírica: Lote 1B (Fase 1)

## 1. Estratégia de Execução (Subetapas)
O objetivo é provar a boundary real com menor atrito e máximo valor probatório.

1. **Subetapa 1 (Prioridade): E2B Sandbox**. Identificado como o candidato de maior prontidão e isolamento físico.
2. **Subetapa 2 (Comparativa):** Só será aberta se houver necessidade de benchmarking secundário após o sucesso da subetapa 1.

## 2. Roteiro Operacional (E2B)
- **Implementação:** Criar `E2BSandboxAdapter` integrando o SDK oficial.
- **FS-ESCAPE (Cloud):** Provar que `ls /` não vê nada do host operacional do orquestrador.
- **SECRET-ESCAPE (Cloud):** Allowlist rígida de ENV; bloqueio de qualquer credencial não-injetada.
- **LIFECYCLE:** Teste explícito de `destroy()` com verificação de resíduos e visibilidade de processos.

## 3. Subetapa 2: Execução Fiscal e Veredito Binário
O objetivo exclusivo é a execução do protocolo endurecido contra o E2B para produzir evidência real.

### Entregáveis Mandatórios
1. **Logs Reais de Execução:** Captura bruta do terminal com timestamps e outputs.
2. **Matriz de Evidências (FS, Rede, Segredos, Lifecycle):** Cruzamento entre o teste e o print/log que prova o isolamento.
3. **Veredito Binário Final:** Classificação irrevogável em **HOMOLOGADO**, **REPROVADO** ou **INCONCLUSIVO**.

### Condição de Avanço
O Lote 2 só será avaliado após a entrega destes três artefatos com sucesso empírico.

## 4. Vereditos Possíveis
- **HOMOLOGADO:** Passa em 100% dos testes do Gate Binário.
- **REPROVADO:** Falha em qualquer vetor de escape (mesmo parcial).
- **INCONCLUSIVO:** Impossibilidade técnica de executar o teste no ambiente disponível (bloqueia o Lote 2).

## 5. Regras de Ouro
- Proibido simular resultados de comandos (`ls`, `curl`, `cat`).
- Proibido usar Mock em substituição ao adaptador no Lote 1B.
- O resultado deve ser exportado via logs reais do shell.
