FROM postgres:14

COPY init.sql /docker-entrypoint-initdb.d/
RUN mkdir /log
RUN chmod -R 777 /log

CMD ["postgres"]


