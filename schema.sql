create table Category(
    id integer PRIMARY KEY,
    name varchar(120) UNIQUE,
    is_base boolean,
    weekly_limit integer
);

create table Budget(
    id integer PRIMARY KEY,
    month_limit integer
);

create table Payment(
    id integer PRIMARY KEY,
    category REFERENCES Category (id) ON DELETE RESTRICT,
    amount integer,
    paid_at datetime
);

insert into Category (name, is_base) values
    ('Products', true),
    ('Cafe', true),
    ('Communal', true),
    ('Entertainment', false),
    ('Transport', false),
    ('Gasoline', false),
    ('Communication', false),
    ('Vacation', false),
    ('Other', false);