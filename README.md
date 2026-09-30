# ServiceFlow - Automação de Chamados Qualitor Web

Sistema de automação corporativa com interface gráfica para abertura, atribuição e encerramento de chamados em lote no sistema **Qualitor Web** da SME-RJ (`helpdesk-sme.netcenter.com.br`).

---

## 🚀 Funcionalidades

- **Interface Gráfica Desktop Moderna** construída em Tkinter (estilo limpo, responsivo, feedback visual em tempo real e barra de progresso).
- **Abertura em Lote**:
  - Seleção dinâmica de CRE (1ª à 11ª CRE + Nível Central).
  - Filtro automático de Unidades/Escolas/Departamentos correspondentes à CRE escolhida.
  - Árvore hierárquica de serviços (Hardware, Manutenção de Ambiente, Antivírus, etc.).
  - Preenchimento e submissão automatizada de formulários dinâmicos (`viewQForm.php`).
  - Atribuição automática do chamado ao usuário logado (`cadastro_chamado.php`).
- **Encerramento Automático Integrado**:
  - Opção de encerrar o chamado imediatamente após a abertura com registro de acompanhamento técnico.
- **Fechar Chamados em Série**:
  - Janela dedicada para colar uma lista de chamados existentes (ex: de relatórios ou planilhas) e realizar o encerramento em massa.
- **Execução Paralela (Multi-robôs)**:
  - Disparo de múltiplos robôs simultâneos com perfis temporários isolados no Microsoft Edge.

---

## 📂 Estrutura do Projeto

```
Abertura-de-chamados/
├── qualitor_gui.py               # Interface gráfica desktop (Tkinter)
├── qualitor_automation.py        # Motor de automação Selenium / Edge
├── departamentos_data.py         # Mapeamento de CREs e Unidades/Escolas
├── service_tree.py               # Árvore de serviços do Qualitor
├── cres_list.py                  # Lista de Coordenadorias Regionais de Educação
├── serviceflow.ico               # Ícone do aplicativo
├── INICIAR_NAVEGADOR_TESTE.bat   # Script para inicialização de Edge com Remote Debugging
├── SERVICEFLOW.bat               # Script para inicialização rápida da aplicação
├── requirements.txt              # Dependências Python
├── GUIA_DESENVOLVIMENTO.md       # Guia completo da arquitetura e próximos passos
└── README.md                     # Documentação geral
```

---

## 🛠️ Como Executar

### 1. Pré-requisitos
- Python 3.10+ instalado.
- Microsoft Edge instalado.

### 2. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 3. Executando o Sistema
Execute via duplo clique no arquivo `SERVICEFLOW.bat` ou pelo terminal:
```bash
python qualitor_gui.py
```

---

## 📝 Documentação Técnica e Manutenção

Para entender os detalhes internos, bugs conhecidos e histórico das versões, consulte o arquivo [GUIA_DESENVOLVIMENTO.md](file:///C:/projetos/Abertura-de-chamados/GUIA_DESENVOLVIMENTO.md).
