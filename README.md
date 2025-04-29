# Reversible image alteration system

A reversible image alteration system, that applies pixel modifications to a selected image and creates a number of variants.
The system allows to select a certain image variant, to check if the applied alterations are reversible.

## Architecture
The system is composed of 3 main services:
- Processing service
- Storage service
- Validation service

The storage service is composed of 2 microservices:
- SQL database
- File storage

Services communicate with the storage via HTTP/2 and database connector

## Prerequisites
- Docker
- docker compose cli

## Setup
1. Clone the git repo
2. In the project root run `./scripts/deploy.sh`, that should build the necessary docker containers for the application

The processing service is available on `0.0.0.0:8000` and validation service on `0.0.0.0:3000`
To test the services go to the designated Swagger documentation for each service - `0.0.0.0:8000/docs` and `0.0.0.0:3000/docs`

## Trying it out

In the Swagger documentation for the processing service `0.0.0.0:8000/docs` upload a random image and press `Execute` like so:

![image](https://github.com/user-attachments/assets/4c99e56f-4326-4215-b718-7b863ceecf73)


It takes roughly ~7-9 seconds to generate all the variants and upload to the storage. You should get a response like this:

![image](https://github.com/user-attachments/assets/fe9ee6b8-ac4d-4697-80f7-df66139895b4)


Taking the `original_image_id` from the response, go to the image validator service docs `0.0.0.0:3000/docs` and test with the `original_image_id`:

![image](https://github.com/user-attachments/assets/59b417e3-55e6-4e6e-b045-1836fdae7d84)


The verifier service generates a response which tells whether the image is reversible or not:

![image](https://github.com/user-attachments/assets/a7a893dd-9412-4d83-8b6b-86eddfdd8929)


To get an unreversible image response, you can try with a JPEG format.

To view the uploaded images, in the project root go to the `./storage/file_storage/` directory.
To view the database go to `http://localhost:5050/`, the login email is `admin@admin.com` and password is `admin`
Database server hostname is `python-image-db` user is `admin` and there is no password.

