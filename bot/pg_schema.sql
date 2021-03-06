create table Category(
    id BIGINT PRIMARY KEY generated always as identity,
    name varchar(120) UNIQUE,
    is_base boolean,
    weekly_limit integer
);

create table Budget(
    id BIGINT PRIMARY KEY generated always as identity,
    month_limit integer NOT NULL,
    balance = integer,
    created_at timestamp NOT NULL,
    expired_at timestamp NOT NULL
);

create table Payment(
    id BIGINT PRIMARY KEY generated always as identity,
    category integer,
    amount integer,
    paid_at timestamp,
    FOREIGN KEY(category) REFERENCES Category (id) ON DELETE RESTRICT
);

create table Aliases(
    id BIGINT PRIMARY KEY generated always as identity,
    category integer,
    alias varchar(120) UNIQUE,
    FOREIGN KEY(category) REFERENCES Category (id) ON DELETE RESTRICT
);

insert into Category (name, is_base) values
    ('products', true),
    ('cafe', true),
    ('communal', true),
    ('medicine', true),
    ('gifts', true),
    ('clothes', true),
    ('entertainment', false),
    ('transport', false),
    ('gasoline', false),
    ('car', false),
    ('communication', false),
    ('vacation', false),
    ('other', false);