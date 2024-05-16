create user repl_user with replication ENCRYPTED PASSWORD 'Qq123456';
select pg_create_physical_replication_slot('replication_slot');


CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS phonenumbers (
    id SERIAL PRIMARY KEY,
    number VARCHAR(20) NOT NULL
);

INSERT INTO Emails (email) VALUES ('test@test.ru');
INSERT INTO PhoneNumbers (number) VALUES ('+7 999 999 99 99');

