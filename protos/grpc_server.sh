# Generate template based on grpc_server.proto's config
# Usage: sh grpc_server.sh
#
# "--proto_path" defines template file's root folder for search
# "-m" defines the template engine
# "--python_out" defines the result output path
# Doc: https://developers.google.com/protocol-buffers/docs/proto3

OUTPUT_DIR=../src/python/server
PROTO_DIR=./
PROTO_FILE=grpc_server.proto
python -m grpc_tools.protoc --proto_path=$PROTO_DIR --python_out=$OUTPUT_DIR --pyi_out=$OUTPUT_DIR --grpc_python_out=$OUTPUT_DIR $PROTO_FILE
