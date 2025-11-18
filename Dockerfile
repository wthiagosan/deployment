# Usa uma imagem base Python leve
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Comando para rodar a aplicação com Uvicorn
# O host 0.0.0.0 é necessário para que o contêiner seja acessível externamente
# A porta 8000 é a porta padrão que o Lightsail Container Service espera
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
