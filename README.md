## Face detection application

### Installation

1. Register at [Face++ User Console](https://console.faceplusplus.com/) and obtain `API Key` and `API Secret` for Detect API in Face Recognition Service.

2. Insert obtained `API Key` and `API Secret` into `./docker/.fpp.template.env` file in the following order:

        FACE_KEY=API Key
        FACE_SECRET= API Secret

3. Create Docker volumes for MinIO and MongoDB data storage: 

        docker volume create minio-data
        docker volume create mongo-data

4. Build and run the application:

        docker-compose build
        docker-compose up -d

### Usage

Usage example is provided in the Jupyter Notebook `./examples/client.ipynb`. To run the example a virtual environment has to be installed and activated, and required packages installed:

        pip install -r ./examples/requirements.txt








