# Bleach — Spiritual Crossroads

A versão de trabalho é esta pasta. Consulte o [README principal](../../README.md) para instalação, controles, personagens, arquitetura e limitações atualizadas.

No Windows, execute `INSTALAR.cmd` e depois `JOGAR.cmd`. Os atalhos usam o ambiente isolado `.venv` na raiz do repositório; o instalador exige que a estrutura do checkout seja preservada.

Alternativa independente: instale `requirements.txt` em um ambiente Python 3.10+ e execute `python game.py`.

Testes: `python -m unittest discover -s tests -v`. Capturas reproduzíveis: `python qa_preview.py`. Resultados: [VALIDACAO.md](VALIDACAO.md).
