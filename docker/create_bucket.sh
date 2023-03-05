#!/bin/bash
/usr/bin/mc config host add minio http://minio:${API_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD};
/usr/bin/mc mb minio/${INITIAL_BUCKET_NAME};
exit 0;