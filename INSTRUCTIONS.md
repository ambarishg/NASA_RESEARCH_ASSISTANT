sudo apt-get update

sudo apt-get install postgresql postgresql-contrib

dpkg --status postgresql

sudo service postgresql start

 ps aux | grep postgres

sudo -u postgres psql

SELECT version();

\l

CREATE TYPE cat_enum AS ENUM ('coffee', 'tea');

CREATE TABLE IF NOT EXISTS cafe (
  id SERIAL PRIMARY KEY,        -- AUTO_INCREMENT integer, as primary key
  category cat_enum NOT NULL,   -- Use the enum type defined earlier
  name VARCHAR(50) NOT NULL,    -- Variable-length string of up to 50 characters
  price NUMERIC(5,2) NOT NULL,  -- 5 digits total, with 2 decimal places
  last_update DATE              -- 'YYYY-MM-DD'
);

 \dt+

\d+ cafe

#########################

sudo -u postgres createuser --login --pwprompt ambarish

sudo -u postgres createdb --owner=ambarish cafe01
sudo -u postgres createdb --owner=ambarish NASADB

sudo service postgresql restart

psql -U ambarish cafe01
psql -U ambarish NASADB

create table if not exists cafe (
           name varchar(50),
           price numeric(5,2),
           primary key (name));

insert into cafe values
           ('Espresso', 3.99),
           ('Green Tea', 2.99);

select * from cafe;