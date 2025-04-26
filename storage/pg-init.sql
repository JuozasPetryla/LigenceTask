CREATE SCHEMA python_image_store;

CREATE USER admin;
ALTER ROLE admin SET search_path = python_image_store;
GRANT ALL ON SCHEMA python_image_store TO admin;
