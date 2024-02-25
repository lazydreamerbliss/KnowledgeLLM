# Generate template based on grpc_server.proto's config
#
# "--proto_path" defines template file's root folder for search
# "-m" defines the template engine
# "--python_out" defines the result output path
# Doc: https://developers.google.com/protocol-buffers/docs/proto3

PROTO_DIR=./protos
SERVER_OUTPUT_DIR=./src/backend/server/grpc
CLIENT_OUTPUT_DIR=./src/launcher/server/grpc

mkdir -p $SERVER_OUTPUT_DIR
mkdir -p $CLIENT_OUTPUT_DIR


# Build server side (Python)
# - Need to install grpcio-tools via pip
python -m grpc_tools.protoc \
    --proto_path=$PROTO_DIR \
    --python_out=$SERVER_OUTPUT_DIR \
    --pyi_out=$SERVER_OUTPUT_DIR \
    --grpc_python_out=$SERVER_OUTPUT_DIR \
    obj_basic.proto \
    obj_shared.proto \
    backend.proto

# Python generated files have issues with import module name, replace "import obj_basic_pb2" to "import server.grpc.obj_basic_pb2"
PY_MODULE_PREFIX="server.grpc"
sed -i "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2_grpc.py
sed -i "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.py
sed -i "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.pyi
sed -i "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2_grpc.py
sed -i "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.py
sed -i "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.pyi


# Build client side (JS)
# - Need to install grpc-tools via npm globally
# - Doc: https://grpc.io/docs/languages/node/basics/
grpc_tools_node_protoc \
    --js_out=import_style=commonjs,binary:$CLIENT_OUTPUT_DIR \
    --grpc_out=grpc_js:$CLIENT_OUTPUT_DIR \
    --proto_path=$PROTO_DIR \
    obj_basic.proto \
    obj_shared.proto \
    backend.proto
