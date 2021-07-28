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
    category integer,
    amount integer,
    paid_at datetime,
    FOREIGN KEY(category) REFERENCES Category(id) ON DELETE RESTRICT
);

insert into Category (name, is_base) values
    ('products', true),
    ('cafe', true),
    ('communal', true),
    ('entertainment', false),
    ('transport', false),
    ('gasoline', false),
    ('communication', false),
    ('vacation', false),
    ('other', false);