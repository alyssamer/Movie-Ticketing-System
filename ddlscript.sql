------------------------------------------
----- TABLES
------------------------------------------

-- client_data.csv -> name, address, email, password, interests, reward_member
CREATE TABLE client (
    name          VARCHAR(255) NOT NULL,
    address       VARCHAR(255),
    email         VARCHAR(255) PRIMARY KEY,
    interests     VARCHAR(255),
    reward_member BOOLEAN NOT NULL DEFAULT FALSE,
    password      VARCHAR(255) NOT NULL
);

-- administrator_data.csv -> email, password
CREATE TABLE administration (
    email    VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

-- theatre_data.csv -> theatre_id, max_occupancy, is_3d, has_fancy_sound
CREATE TABLE theatre (
    theatre_id      INTEGER PRIMARY KEY,
    max_occupancy   INTEGER NOT NULL CHECK (max_occupancy > 0),
    is_3d           BOOLEAN NOT NULL DEFAULT FALSE,
    has_fancy_sound BOOLEAN NOT NULL DEFAULT FALSE
);

-- movies.csv -> movie_id,title, is_major_studio, release_date, length, original_language, genre
CREATE TABLE movies (
    movie_id          INTEGER PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    is_major_studio   BOOLEAN NOT NULL DEFAULT FALSE,
    release_date      DATE NOT NULL,
    length            INTEGER NOT NULL CHECK (length > 0),
    original_language VARCHAR(100) NOT NULL,
    genre             VARCHAR(100) NOT NULL
);

-- person_data.csv -> person_id, name, birthdate, biography
CREATE TABLE persons (
    person_id INTEGER PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    birthdate DATE,
    biography TEXT
);

-- payment_methods.csv -> client_email, type, card_number, billing_address
CREATE TABLE payment_method (
    client_email    VARCHAR(255) NOT NULL,
    type            VARCHAR(20) NOT NULL,
    card_number     VARCHAR(30) PRIMARY KEY,
    billing_address VARCHAR(255),
    CONSTRAINT fk_payment_method_client
        FOREIGN KEY (client_email)
        REFERENCES client(email)
        ON DELETE CASCADE,
    CONSTRAINT chk_payment_type
        CHECK (type IN ('credit', 'debit'))
);

-- awards_data.csv -> award_id, title, year, person_id, role, movie_id
CREATE TABLE awards (
    award_id  INTEGER PRIMARY KEY,
    title     VARCHAR(255) NOT NULL,
    year      INTEGER NOT NULL CHECK (year >= 1900),
    person_id INTEGER NOT NULL,
    role      VARCHAR(50) NOT NULL,
    movie_id  INTEGER NOT NULL,
    CONSTRAINT fk_awards_person
        FOREIGN KEY (person_id)
        REFERENCES persons(person_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_awards_movie
        FOREIGN KEY (movie_id)
        REFERENCES movies(movie_id)
        ON DELETE CASCADE
);

-- screening_data.csv -> screening_id, movie_id, theatre_id, date, time
CREATE TABLE screening_schedule (
    screening_id INTEGER PRIMARY KEY,
    movie_id     INTEGER NOT NULL,
    theatre_id   INTEGER NOT NULL,
    date         DATE NOT NULL,
    time         TIME NOT NULL,
    CONSTRAINT fk_screening_movie
        FOREIGN KEY (movie_id)
        REFERENCES movies(movie_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_screening_theatre
        FOREIGN KEY (theatre_id)
        REFERENCES theatre(theatre_id)
        ON DELETE CASCADE
);

-- movie_available_language.csv -> movie_id, available_language
CREATE TABLE movie_available_language (
    movie_id           INTEGER NOT NULL,
    available_language VARCHAR(100) NOT NULL,
    PRIMARY KEY (movie_id, available_language),
    CONSTRAINT fk_movie_language_movie
        FOREIGN KEY (movie_id)
        REFERENCES movies(movie_id)
        ON DELETE CASCADE
);

-- ticket_sales.csv -> sale_id, quantity_sold, ticket_price, client_email, card_number
CREATE TABLE ticket_sales (
    sale_id       INTEGER PRIMARY KEY,
	screening_id INTEGER NOT NULL,
    quantity_sold INTEGER NOT NULL CHECK (quantity_sold > 0),
    ticket_price  NUMERIC(8,2) NOT NULL CHECK (ticket_price >= 0),
    client_email  VARCHAR(255),
    card_number   VARCHAR(30),
	CONSTRAINT fk_ticket_sales_screening
	    FOREIGN KEY (screening_id)
	    REFERENCES screening_schedule(screening_id)
	    ON DELETE CASCADE, 
    CONSTRAINT fk_ticket_sales_client
        FOREIGN KEY (client_email)
        REFERENCES client(email)
        ON DELETE SET NULL,
    CONSTRAINT fk_ticket_sales_payment
        FOREIGN KEY (card_number)
        REFERENCES payment_method(card_number)
        ON DELETE SET NULL
);


-- movie_role.csv -> role_id, person_id, movie_id, role_type, character_name
CREATE TABLE movie_role (
    role_id        INTEGER PRIMARY KEY,
    person_id      INTEGER NOT NULL,
    movie_id       INTEGER NOT NULL,
    role_type      VARCHAR(20) NOT NULL,
    character_name VARCHAR(255),
    CONSTRAINT fk_movie_role_person
        FOREIGN KEY (person_id)
        REFERENCES persons(person_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_movie_role_movie
        FOREIGN KEY (movie_id)
        REFERENCES movies(movie_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_role_type
        CHECK (role_type IN ('director', 'actor', 'writer', 'producer'))
);
