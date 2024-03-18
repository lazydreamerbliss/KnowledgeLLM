# Generate template based on grpc_server.proto's config
#
# "--proto_path" defines template file's root folder for search
# "-m" defines the template engine
# "--python_out" defines the result output path
# Doc: https://developers.google.com/protocol-buffers/docs/proto3

#######################################
#   Build server side (Python) code   #
#######################################

# Current working directory is at root of the whole project
PROTO_DIR=./protos
SERVER_OUTPUT_DIR=./src/backend/server/grpc
mkdir -p $SERVER_OUTPUT_DIR

# Need to install grpcio-tools
python -m grpc_tools.protoc \
    --proto_path=$PROTO_DIR \
    --python_out=$SERVER_OUTPUT_DIR \
    --pyi_out=$SERVER_OUTPUT_DIR \
    --grpc_python_out=$SERVER_OUTPUT_DIR \
    obj_basic.proto \
    obj_shared.proto \
    backend.proto

# Python generated files have issues with import module name, replace "import obj_basic_pb2" to "import server.grpc.obj_basic_pb2"
# - Using `-i'' -e` in `sed` command is for GNU and BSD compatibility:
#   - https://stackoverflow.com/questions/5694228/sed-in-place-flag-that-works-both-on-mac-bsd-and-linux
#   - https://stackoverflow.com/questions/4247068/sed-command-with-i-option-failing-on-mac-but-works-on-linux
PY_MODULE_PREFIX="server.grpc"
sed -i'' -e "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2_grpc.py
sed -i'' -e "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.py
sed -i'' -e "s/import obj_basic_pb2/import $PY_MODULE_PREFIX.obj_basic_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.pyi
sed -i'' -e "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2_grpc.py
sed -i'' -e "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.py
sed -i'' -e "s/import obj_shared_pb2/import $PY_MODULE_PREFIX.obj_shared_pb2/g" $SERVER_OUTPUT_DIR/backend_pb2.pyi


#######################################
#     Build client side (JS) code     #
#######################################

# Change working directory to root of launcher project
LAUNCHER_DIR=./src/launcher
cd $LAUNCHER_DIR

# Change proto file's relative path
PROTO_DIR=../../protos
CLIENT_OUTPUT_DIR=./server/grpc
mkdir -p $CLIENT_OUTPUT_DIR

# Need to install `grpc-tools` (DEV), this provides a global command `grpc_tools_node_protoc`
# - Doc: https://grpc.io/docs/languages/node/basics/
npx grpc_tools_node_protoc \
    --js_out=import_style=commonjs,binary:$CLIENT_OUTPUT_DIR \
    --grpc_out=grpc_js:$CLIENT_OUTPUT_DIR \
    --proto_path=$PROTO_DIR \
    obj_basic.proto \
    obj_shared.proto \
    backend.proto

# Build client side (TS) code for type
# - Additionally install plugin `grpc_tools_node_protoc_ts` (DEV) to generate TypeScript definition
# - Doc: https://www.npmjs.com/package/grpc_tools_node_protoc_ts
LAUNCHER_NODE_MODULES_FOLDER=./node_modules
npx protoc \
    --plugin=protoc-gen-ts=$LAUNCHER_NODE_MODULES_FOLDER/.bin/protoc-gen-ts \
    --ts_out=$CLIENT_OUTPUT_DIR \
    --proto_path=$PROTO_DIR \
    obj_basic.proto \
    obj_shared.proto \
    backend.proto
