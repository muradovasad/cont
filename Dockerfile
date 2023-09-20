FROM python:3.11 as compiler
ENV PYTHONUNBUFFERED 1

RUN mkdir content_module
WORKDIR /content_module/

RUN python3 -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# install psycopg2 dependencies
# RUN apt update \ && apt add postgresql-dev gcc python3-dev musl-dev

# install requirements
RUN pip install --upgrade pip
COPY ./requirements.txt /content_module/requirements.txt
RUN pip install -Ur requirements.txt

EXPOSE 8033

COPY . /content_module/
# CMD python3 manage.py runserver 0.0.0.0:8022
