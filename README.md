## Como Executar a Aplicação de Controle de Temperatura

Este projeto consiste em uma aplicação de controle de temperatura distribuída em três componentes principais: CLP (clp.py), MES (mes.py) e Planta (planta.py). O arquivo sinotico.py serve como interface para o usuário interagir com o sistema.


### Clone o Projeto

#### ```bash
  git clone https://github.com/PabloRMCarneiro/opc-ua-blast-furnace
  ```

### Configuração do Ambiente

#### Criar um Ambiente Virtual

Um ambiente virtual Python permite isolar as dependências do projeto do seu ambiente Python global. Isso evita conflitos de bibliotecas e facilita o gerenciamento das dependências do projeto.

**Opção 1: Usando venv (Recomendado)**

Abra um terminal na raiz do projeto.

Crie um ambiente virtual chamado env:
```bash
python3 -m venv env
```

Ative o ambiente virtual:
- Linux/macOS:
  ```bash
  source env/bin/activate
  ```
- Windows:
  ```bash
  env\Scripts\activate
  ```

**Opção 2: Usando virtualenv**

Se você não tiver o venv instalado, você pode usar o virtualenv:

Instale o virtualenv:
```bash
pip install virtualenv
```

Crie um ambiente virtual chamado env:
```bash
virtualenv env
```

Ative o ambiente virtual (mesmo processo da opção 1).

### Configurações do Ambiente

**Crie um arquivo .env**

- Crie um arquivo chamado .env na raiz do projeto.
- Dentro do arquivo, defina as seguintes variáveis de ambiente:
    - **HOST:** Endereço IP do servidor (CLP) Ex: '127.0.0.1'
    - **PORT:** Porta do servidor (CLP) Ex: 12345
    - **SERVER_ENDPOINT_OPC:** Endpoint do servidor OPC UA = 'opc.tcp://127.0.0.1:53530/freeopcua/server/'
    - **NODE_TEMPERATURE:** Node ID do valor da temperatura no servidor OPC UA = 'ns=2;i=2'
    - **NODE_REF_TEMPERATURE:** Node ID do valor da temperatura de referência no servidor OPC UA = 'ns=2;i=3'
    - **NODE_HEAT_FLOW:** Node ID do valor do fluxo de calor no servidor OPC UA = 'ns=2;i=4'
    - **NODE_KP:** Node ID do valor do parâmetro KP do controlador PID no servidor OPC UA = 'ns=2;i=5'
    - **NODE_KI:** Node ID do valor do parâmetro KI do controlador PID no servidor OPC UA = 'ns=2;i=6'
    - **NODE_KD:** Node ID do valor do parâmetro KD do controlador PID no servidor OPC UA = 'ns=2;i=7'

#### Instalar Dependências

Com o ambiente virtual ativado, instale as bibliotecas listadas no arquivo requirements.txt:
```bash
pip install -r requirements.txt
```

Este comando instalará todas as bibliotecas necessárias para executar a aplicação.

### Executando a Aplicação

Lembre-se sempre que, ao abrir um novo terminal sempre ativar o ambiente virtual novamente

#### Inicie o OPC SERVER:

Abra um terminal na raiz do projeto.
O servidor ficará disponível nesse endpoint: `opc.tcp://127.0.0.1:53530/freeopcua/server/`
Os nodes_ids criados das variáveis estão apresentados no tópico: Crie um arquivo .env

Execute o comando:
```bash
python opc_server.py
```

#### Inicie a PLANTA:

Abra um terminal na raiz do projeto.

Execute o comando:
```bash
python planta.py
```

A planta irá simular o processo de aquecimento, controlando a temperatura com base na temperatura de referência e nos parâmetros PID recebidos do CLP.

A planta também enviará os valores de temperatura e fluxo de calor para o servidor OPC UA.

#### Inicie o MES:

Abra um novo terminal na raiz do projeto.

Execute o comando:
```bash
python mes.py
```

O MES irá se conectar ao servidor OPC UA e registrará os valores de temperatura em um arquivo mes.txt.

#### Inicie a CLP:

Abra um novo terminal na raiz do projeto.

Execute o comando:
```bash
python clp.py
```

O CLP iniciará um servidor que receberá comandos do sinotico.py e enviará dados para o MES (mes.py).



#### Inicie o Sinótico (Interface):

Abra um novo terminal na raiz do projeto.

Execute o comando:
```bash
streamlit run sinotico.py
```

O sinótico irá se conectar ao servidor do CLP e permitirá que você:
- Defina a temperatura de referência.
- Ajuste os parâmetros KP, KI e KD do controlador PID.
- As informações de temperatura serão exibidas em uma interface web via streamlit.


### Observações

- Certifique-se de que todas as portas e endereços IP estejam configurados corretamente no arquivo .env e nos scripts.
- O servidor OPC UA deve estar em execução antes de iniciar a aplicação.
- A simulação da planta é um modelo simplificado e pode não representar um processo real com precisão.

#### Arquivos de Log

- O arquivo log_error.txt registrará quaisquer erros que ocorrerem durante a execução da aplicação.
- O arquivo mes.txt registrará os valores de temperatura recebidos do servidor OPC UA pelo MES.
- O arquivo historiar.txt registrará todos os valores recebidos do clp.py pelo SINOTIPO.

### Dicas de Uso

- Use o sinótico para ajustar a temperatura de referência e os parâmetros PID para atingir a temperatura desejada.
- Observe o comportamento da planta e ajuste os parâmetros conforme necessário.
- O arquivo mes.txt pode ser usado para analisar o histórico de temperaturas e avaliar o desempenho do sistema.

