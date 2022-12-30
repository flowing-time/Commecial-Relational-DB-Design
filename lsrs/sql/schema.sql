DROP DATABASE IF EXISTS `cs6400_team048`; 
SET default_storage_engine=InnoDB;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS cs6400_team048 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;
USE cs6400_team048;

-- Tables
CREATE TABLE State (
  name varchar(128) NOT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE City (
  name varchar(128) NOT NULL,
  state varchar(128) NOT NULL,
  population int(16) NOT NULL,
  PRIMARY KEY (name, state),
  CONSTRAINT fk_City_state_State_name FOREIGN KEY (state) REFERENCES State (name)
);

CREATE TABLE Date (
  date date NOT NULL,
  PRIMARY KEY (date)
);

CREATE TABLE Holiday (
  date date NOT NULL,
  name varchar(128) NOT NULL,
  PRIMARY KEY (date, name),
  CONSTRAINT fk_Holiday_date_Date_date FOREIGN KEY (date) REFERENCES Date (date)
);

CREATE TABLE Product (
  pid varchar(128) NOT NULL,
  name varchar(128) NOT NULL,
  retail_price float NOT NULL,
  PRIMARY KEY (pid)
);

CREATE TABLE Discount (
  product varchar(128) NOT NULL,
  date date NOT NULL,
  discount_price float NOT NULL,
  PRIMARY KEY (product, date),
  CONSTRAINT fk_Discount_product_Product_pid FOREIGN KEY (product) REFERENCES Product (pid),
  CONSTRAINT fk_Discount_date_Date_date FOREIGN KEY (date) REFERENCES Date (date)
);

CREATE TABLE Category (
  name varchar(128) NOT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE ProductCategory (
  product varchar(128) NOT NULL,
  category varchar(128) NOT NULL,
  PRIMARY KEY (product, category),
  CONSTRAINT fk_ProductCategory_product_Product_pid FOREIGN KEY (product) REFERENCES Product (pid),
  CONSTRAINT fk_ProductCategory_category_Category_name FOREIGN KEY (category) REFERENCES Category (name)
);

CREATE TABLE Childcare (
  time_limit int(16) NOT NULL,
  PRIMARY KEY (time_limit)
);

CREATE TABLE Store (
  store_number varchar(128) NOT NULL,
  phone_number varchar(128) NOT NULL,
  street_address varchar(128) NOT NULL,
  city varchar(128) DEFAULT NULL,
  state varchar(128) DEFAULT NULL,
  restaurant tinyint(1) DEFAULT 0,
  snack_bar tinyint(1) DEFAULT 0,
  childcare_time int(16) DEFAULT NULL,
  PRIMARY KEY (store_number),
  CONSTRAINT fk_Store_childcare_time_Childcare_time_limit FOREIGN KEY (childcare_time) REFERENCES Childcare (time_limit)
);

CREATE TABLE Sale (
  product varchar(128) NOT NULL,
  store varchar(128) NOT NULL,
  date date NOT NULL,
  quantity int(16) NOT NULL,
  PRIMARY KEY (product, store, date),
  CONSTRAINT fk_Sale_store_Store_store_number FOREIGN KEY (store) REFERENCES Store (store_number),
  CONSTRAINT fk_Sale_product_Product_pid FOREIGN KEY (product) REFERENCES Product (pid),
  CONSTRAINT fk_Sale_date_Date_date FOREIGN KEY (date) REFERENCES Date (date)
);

CREATE TABLE Campaign (
  date date NOT NULL,
  name varchar(128) NOT NULL,
  PRIMARY KEY (date, name),
  CONSTRAINT fk_Campaign_date_Date_date FOREIGN KEY (date) REFERENCES Date (date)
);