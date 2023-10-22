# Perguntas.io

Um site de perguntas e respostas escrito em Python/Django.

## Começando

Estas instruções fornecerão uma cópia do projeto em funcionamento em seu computador local para fins de desenvolvimento e teste.

`git clone https://github.com/augusto71/qa`

`pip3 install -r requirements.txt`

`python3 manage.py makemigrations`

`python3 manage.py migrate`

Crie um arquivo chamado `.env` na raíz do projeto (onde fica o script `manage.py`) com o seguinte conteúdo:

SECRET_KEY = 'chave-secreta-aqui'

Para rodar o servidor local, use:

`python3 manage.py runserver`

E para acessar o site, use o domínio `127.0.0.1` na porta 8000:

`http://127.0.0.1:8000`

### Pré-requisitos

Os pré-requisitos estão no arquivo requirements.txt na raíz do projeto.

## Construído Com

* [Django](https://www.djangoproject.com/) - O framework web usado

## Author

* [Erick Augusto](https://github.com/augusto71)
