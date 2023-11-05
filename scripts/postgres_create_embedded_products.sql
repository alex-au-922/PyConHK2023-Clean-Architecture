CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS EMBEDDED_PRODUCTS (
    product_id CHAR(10) NOT NULL,
    embedding vector(384) NOT NULL,
    modified_date TIMESTAMP NOT NULL,
    created_date TIMESTAMP NOT NULL,
    PRIMARY KEY (product_id)
);