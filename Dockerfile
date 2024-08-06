FROM python:3.10

WORKDIR /code

COPY ./docker_requirements.txt /code/docker_requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/docker_requirements.txt
#ENV HOST_DB=host.docker.internal
COPY ./app /code/app
COPY alembic.ini /code/
#COPY .env.sample /code/
#COPY .env.docker /code/
#RUN cd app
#RUN alembic upgrade head

#CMD ["fastapi", "run", "app/main.py", "--port", "80"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]