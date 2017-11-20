FROM python:3
RUN mkdir -p /app/bl3trader
ADD . /app/bl3trader
WORKDIR /app/bl3trader
CMD ["make"]
