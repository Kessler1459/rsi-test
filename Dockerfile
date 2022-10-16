FROM python:3.10-slim-buster

ADD . .

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

ENV RSI_API_KEY=
ENV PAIR=
ENV INITIAL_USDT=
ENV INITIAL_CRYPTO=

EXPOSE 8000

RUN ["chmod", "+x", "./run.sh"]
CMD ./run.sh