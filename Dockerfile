FROM python:3

WORKDIR /usr/src/app

RUN pip install selenium
RUN pip install flask
COPY main.py ./

CMD [ "python", "./main.py" ]
