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

# Build server side (Python) code
# - Need to install grpcio-tools
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
sed -i '' -e "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2_grpc.py
sed -i '' -e "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.py
sed -i '' -e "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.pyi
sed -i '' -e "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2_grpc.py
sed -i '' -e "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.py
sed -i '' -e "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.pyi

# Build client side (JS) code
# - Need to install grpc-tools
# - Doc: https://grpc.io/docs/languages/node/basics/
grpc_tools_node_protoc \
    --js_out=import_style=commonjs,binary:$CLIENT_OUTPUT_DIR \
    --grpc_out=grpc_js:$CLIENT_OUTPUT_DIR \
    --proto_path=$PROTO_DIR \
    obj_basic.proto \
    obj_shared.proto \
    backend.proto

# Build client side (TS) code for type
# - Additionally install grpc_tools_node_protoc_ts (DEV) to generate TypeScript definition
# - Doc: https://www.npmjs.com/package/grpc_tools_node_protoc_ts
LAUNCHER_NODE_MODULES_FOLDER=./src/launcher/node_modules
protoc \
    --plugin=protoc-gen-ts=$LAUNCHER_NODE_MODULES_FOLDER/.bin/protoc-gen-ts \
    --ts_out=$CLIENT_OUTPUT_DIR \
    --proto_path=$PROTO_DIR \
    obj_basic.proto \
    obj_shared.proto \
    backend.proto
