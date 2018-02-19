######################################################
########### OPINION MINING - DOCUMENTATION ###########
######################################################

1. Faça download da versão mais recente do Python.
Link: https://www.python.org/downloads/release/python-364/
OBS: Antes da instalação do Python, certifique-se de marcar a opção "Add Python 3.6 to PATH" no instalador.
OBS2: Ao final da instalação, selecione a opção "Disable path length limit".


2. Faça download do PyCharm versão Community, IDE para desenvolvimento Python.
Link: https://www.jetbrains.com/pycharm/download


3. Após instalar o PyCharm, abra e selecione "Create New Project".


4. No nome do projeto, substitua "/untitled" por "/Opinion Mining" e clique em avançar/concluir.
OBS: Armazene o path de onde o projeto foi criado.


5. Faça download Git Bash, console que irá auxiliar na utilização do Git.
Link: https://git-scm.com/download


6. Após instalar procure no inicializar por Git Bash e abra o programa.


7. Uma vez no console, digite: "cd C:" (Pode trocar C: para o disco de preferencia do sistema).


8. Digite a seguinte sequencia de comandos:
mkdir Git
cd Git
git clone https://github.com/diegobrzk/opinion-mining.git


9. Uma vez com o repositório em sua máquina, faça download da ferramenta HardLinkShell, a qual permite realizarmos o vínculo simbólico de arquivos com facilidade.
Link: http://schinagl.priv.at/nt/hardlinkshellext/linkshellextension.html#download


10. Após instalado, abra o seguinte path (substitua o disco C: pelo disco escolhido) em seu explorer.
Path: C:/Git/opinion-mining


11. Clique com o botão direito na pasta "src" e selecione a opção criar "Selecionar a origem do vínculo".


12. Vá até o path onde seu projeto do PyCharm foi criado.
EX: C:/Users/Diego.Santos/PyCharmProjects/Opinion Mining/venv/Scripts


13. Clique com o botão direito dentro da pasta e selecione a opção "Soltar como..." e depois "Vínculo Simbólico".


14. Feito isso, iremos instalar alguns imports necessários para esse projeto, para isso, no PyCharm clique em "File" e depois em "Settings".


15. Clique em "Project: Opinion Mining" e depois em "Project Interpreter", clique no "+" do lado direito da tabela e adicione os seguintes pacotes:
pytube
xmltodict
textblob
pydub
pyAudioAnalysis
imageio
moviepy
librosa
cv2

16. Instale o ffmpeg.
Link: https://ffmpeg.zeranoe.com/builds/
Tutorial: https://pt.wikihow.com/Instalar-o-FFmpeg-no-Windows


17. Após isso, concluímos a instalação. Para executar o projeto, vá até o PyCharm, no projeto Opinion Mining, vá até a pasta "venv/Scripts/src/br/edu/fei/opinion/mining", clique com o botão direito em "main.py" e selecione "Run 'main'".