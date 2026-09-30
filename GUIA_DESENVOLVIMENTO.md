# GUIA DE DESENVOLVIMENTO - SERVICEFLOW

Este guia foi elaborado para documentar a análise reversa, o funcionamento interno, os problemas diagnosticados e os próximos passos para dar continuidade imediata ao projeto **ServiceFlow**.

---

## 1. Contexto e Origem do Código

O projeto estava originalmente disponibilizado apenas em formato binário compilado (`.exe`), contendo duas versões:
1. **Versão Antiga (`c:\projetos\dist\ServiceFlow.exe`)**:
   - Compilada em julho/agosto de 2026.
   - Apresentava falhas graves de concorrência (`bind error 0x2740` ao tentar abrir múltiplos robôs na mesma porta), seletores de serviços desatualizados e ausência de encerramento em série.
2. **Versão Mais Nova (`dist_novo\ServiceFlow.exe` e `dist.zip`)**:
   - Compilada em 23/09/2026 com isolamento de perfis temporários (`tempfile.mkdtemp()`) e interface modal para encerramento de chamados.
   - Porém, apresentava falhas no processamento em lote (>1 chamado por robô) e continha o script `INICIAR_NAVEGADOR_TESTE.bat` cuja integração com o código Python ainda não havia sido finalizada.

O código-fonte integral em Python (`.py`) foi recuperado, corrigido, limpo e validado via AST (Abstract Syntax Tree), encontrando-se 100% legível e executável nesta pasta.

---

## 2. Mapa dos Arquivos do Projeto

| Arquivo | Descrição |
| :--- | :--- |
| `qualitor_gui.py` | Interface gráfica em Tkinter (estilo moderno, seleção de CRE/Escola/Serviço, barra de progresso, console de log e diálogo para encerramento em série). |
| `qualitor_automation.py` | Classe `QualitorAutomation` que orquestra o Selenium WebDriver, manipula os iframes (`framePrincipal`), dispara scripts AJAX e gere os workers concorrentes. |
| `departamentos_data.py` | Dicionários `DEPARTAMENTOS_POR_CRE` e `CRE_VALUE_TO_PREFIX` com centenas de unidades escolares e setores cadastrados na SME-RJ. |
| `service_tree.py` | Dicionário hierárquico `SERVICE_TREE` com os códigos de serviços pai e folha do Qualitor. |
| `cres_list.py` | Lista `CRES` mapeando os códigos de 1 a 12 (1ª à 11ª CRE + Nível Central). |
| `INICIAR_NAVEGADOR_TESTE.bat` | Script batch para iniciar o Edge com porta de depuração remota 9222. |
| `SERVICEFLOW.bat` | Script batch para iniciar o aplicativo diretamente no ambiente local. |

---

## 3. Onde Paramos: Diagnóstico dos Problemas Críticos

### Problema 1: Bug da Sessão Perdida (`invalid session id`) no Loop de Chamados
- **Causa Raiz**: Quando um robô processa mais de 1 chamado (ex: lote de 100 chamados distribuídos para 5 robôs = 20 chamados cada), o código tenta fechar popups excedentes e recarregar a árvore de serviços chamando `_reload_root_services()`. Se o Qualitor fechar a janela principal ou houver timeout, o driver perde a sessão.
- **Onde ocorre**: No método `_create_multiple_parallel` (função interna `worker_task`), bloco `except Exception as e:` (linhas ~450-480 de `qualitor_automation.py`).
- **Comportamento atual**: O código loga `[Robô X] Aviso reload: Message: invalid session id... tentando re-navegar...`, mas continua executando o loop no **mesmo driver morto**.
- **Solução a implementar**: Quando a exceção for `InvalidSessionIdException` ou o driver perder comunicação, executar `worker.close()`, recriar `worker.start_browser()`, `worker.login()`, `worker.menu_navigate()` e só então prosseguir com o próximo item da fila.

---

### Problema 2: Modo de Conexão ao Navegador Aberto (`INICIAR_NAVEGADOR_TESTE.bat`)
- **Causa Raiz**: O script `.bat` foi criado com o comando:
  ```bat
  start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\edge_debug_profile" "https://helpdesk-sme.netcenter.com.br/login.php"
  ```
  Isso permite que o usuário faça login manualmente, resolva eventuais captchas corporativos ou problemas de certificado.
- **Onde falta implementar**: No método `start_browser()` de `qualitor_automation.py` e na interface `qualitor_gui.py`:
  - Adicionar na interface uma caixa de seleção: `[ ] Conectar ao Edge já aberto (Porta 9222)`.
  - No `start_browser()`:
    ```python
    if self.use_remote_debugging:
        opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    ```
  - Quando essa opção estiver ativada, o robô não precisa de `usuario` e `senha`, nem de executar `login()`, podendo ir direto para `menu_navigate()`!

---

### Problema 3: Bloqueio do Antivírus Trend Micro Apex One
- **Diagnóstico**: O ambiente corporativo possui o software **Trend Micro Apex One**, que apaga executáveis `.exe` gerados via PyInstaller que não sejam assinados digitalmente.
- **Recomendação**: Para o desenvolvimento e execução diária, o ideal é **rodar diretamente em Python via `SERVICEFLOW.bat`** (usando o interpretador oficial instalado na máquina), eliminando a necessidade de compilação de binários `.exe` que geram falsos positivos no antivírus.

---

## 4. Roteiro Passo a Passo para Continuar

1. **Testar a GUI Localmente**:
   - Abrir o terminal na pasta `C:\projetos\Abertura-de-chamados`.
   - Executar `python qualitor_gui.py` e verificar a abertura da janela.
2. **Implementar a Resiliência de Sessão no `worker_task`**:
   - No loop `while True:` de `worker_task` em `_create_multiple_parallel` e `_close_multiple_parallel`:
     Detectar se a conexão com o navegador falhou e reinicializar a instância do Edge automaticamente.
3. **Adicionar o Modo "Navegador Conectado (Porta 9222)"**:
   - Permitir que o operador clique em `INICIAR_NAVEGADOR_TESTE.bat`, faça o login manual no Qualitor e, no ServiceFlow, apenas clique em "Iniciar" para disparar a automação na janela aberta.
4. **Validar com Chamados Reais em Lote**:
   - Testar sequencialmente (1 a 5 chamados).
   - Testar paralelo (2 a 4 robôs simultâneos).
