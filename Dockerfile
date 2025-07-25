From python:3.6.8
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=shopify_api.settings
WORKDIR /usr/src/app
COPY ./shopify-api/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir /root/logs
