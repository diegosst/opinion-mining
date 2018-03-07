# Opinion Mining

## Setup

Para rodar o projeto, algumas coisas precisam ser previamente instaladas.
  - Anaconda + Python 3.6
  - MongoDB
  - FFMPEG
  - PyCharm
  - Git
  - HardLinkShell

#### Anaconda
Para instalar o Anaconda, faça o download da versão que contém o python 3.6 a partir da seguinte URL:
https://www.anaconda.com/download/
OBS: Lembre-se de marcar a opção que adiciona o Python no PATH da máquina.

### MongoDB
Para instalar o MongoDB, faça o download a partir da seguinte URL, na aba Community Server:
https://www.mongodb.com/download-center#community
OBS: Necessário criar o diretório "C:\data\db" para que o banco funcione.

### FFMPEG
Para instalar o FFMPEG, faça o download a partir da seguinte URL:
https://ffmpeg.zeranoe.com/builds/
Siga o seguinte tutorial para realizar a instalação corretamente:
https://pt.wikihow.com/Instalar-o-FFmpeg-no-Windows

### PyCharm
Para instalar o PyCharm, faça o download a partir da seguinte URL:
https://www.jetbrains.com/pycharm/download/

Após instalar o PyCharm, abra e selecione "Create New Project".

No nome do projeto, substitua "/untitled" por "/Opinion Mining" e clique em avançar/concluir.
OBS: Armazene o path de onde o projeto foi criado.

Agora vá em "File -> Settings -> Project:Opinion Mining -> Project Interpreter".
   - Ao lado da caixa de seleção "Project Interpreter", clique no botão de "engrenagem".
   - Selecione "Show All...".
   - Clique em "+" na barra lateral direita da janela aberta.
   - Selecione "Add Local...".
   - Na janela aberta, selecione "New Environment"
   - Em "Location" coloque o path do "venv" do seu projeto, EX: "C:\Projects\Opinion Mining\venv".
   - Em "Base Interpreter" coloque o path do arquivo python.exe do Anaconda, EX: "C:\Anaconda3\python.exe".
   - Confirme todas as telas até voltar a tela inicial da IDE.

### Git
Para instalar o Git Bash, faça o download a partir da seguinte URL:
https://git-scm.com/download

Após instalar procure no inicializar por Git Bash e abra o programa.

Uma vez no console, digite: "cd C:" (Pode trocar C: para o disco de preferência do sistema).
Digite a seguinte sequencia de comandos:
   - mkdir Git
   - cd Git
   - git clone https://github.com/diegobrzk/opinion-mining.git

Execute também os seguintes comandos para baixar as dependências do projeto:
   - cd C:/Git/opinion-mining
   - pip install -r requirements.txt

### HardLinkShell
Para instalar o Git Bash, faça o download a partir da seguinte URL:
http://schinagl.priv.at/nt/hardlinkshellext/linkshellextension.html#download

Após instalado, abra o seguinte path (pode substituir o disco C: pelo disco escolhido) em seu explorer.
EX: C:/Git/opinion-mining

Clique com o botão direito na pasta "src" e selecione a opção criar "Selecionar a origem do vínculo".

Vá até a pasta Scripts do path em que seu projeto do PyCharm foi criado.
EX: C:\Projects\Opinion Mining\venv\Scripts

Clique com o botão direito dentro da pasta e selecione a opção "Soltar como..." e depois "Vínculo Simbólico".

Com isso concluímos a instalação.

Para executar o projeto, abra o PyCharm e vá até a pasta "Scripts/src" do seu projeto :
EX: C:\Projects\Opinion Mining\venv\Scripts\src
Clique com o botão direito em "main.py" e selecione "Run 'main'".

