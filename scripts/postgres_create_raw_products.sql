CREATE TABLE IF NOT EXISTS RAW_PRODUCTS (
    product_id CHAR(10) NOT NULL,
    name VARCHAR(256) NOT NULL,
    main_category VARCHAR(128) NOT NULL,
    sub_category VARCHAR(128) NOT NULL,
    image_url VARCHAR(256) NOT NULL,
    ratings DECIMAL(2,1) NOT NULL,
    discount_price DECIMAL(10,2) NOT NULL,
    actual_price DECIMAL(10,2) NOT NULL,
    modified_date TIMESTAMP NOT NULL,
    created_date TIMESTAMP NOT NULL,
    PRIMARY KEY (product_id)
);