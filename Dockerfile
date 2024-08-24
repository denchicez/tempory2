FROM python:3.8-slim-buster

# Устанавливаем рабочую директорию в контейнере в /app
WORKDIR /app

# Установите зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Делаем порт 8000 доступным для внешнего мира
EXPOSE 8000

# Копируем содержимое текущей директории в контейнер в /app
COPY . /app

# Устанавливаем PYTHONPATH
ENV PYTHONPATH /app/src

# Запускаем приложение при запуске контейнера
#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]