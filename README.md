# Osoci
Automatizador de análises de open sim a partir de arquivos open cap

## Instalação:
### Ambiente virtual
- Faça o download dos arquivos no repositório
- Instale python 3.8 em sua máquina [Instalação windows store](https://apps.microsoft.com/detail/9mssztt1n39l?hl=pt-br&gl=BR)
- Pelo terminal, navegue até a pasta osoci (não altere a ordem dos comandos):
  - ```pip install venv```
  - ```python3.8 -m venv ososci_venv```
  - ```.\ososci_venv\Scripts\activate```
  - ```python -m pip install -U pip==24.0```
  - ```pip install numpy==1.24.4```
  - ```pip install setuptools==56.0.0```

### Bidings open sim
- Em uma janela de termial:
  - ```cd '<OPENSIM_INSTALL_DIR>\sdk\Python'```
  - ```python setup_win_python38.py```
  - ```python -m pip install .```

## Utilização
- Pelo terminal, navegue até a pasta osoci:
  - ative o ambiente virtual: ```./ososci_venv/Scripts/activate```
  - Adicione as pastas de arquivos open cap a serem analisados na pasta __osoci/data__ 
  - Adicione ao arquivo __setup.json__ os nomes de pastas e arquivos a serem analisados
  - execute o programa: ```python main.py``` 
