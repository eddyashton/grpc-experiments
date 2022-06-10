SCRIPTS_DIR=$( dirname ${BASH_SOURCE[0]} )
ROOT_DIR="$SCRIPTS_DIR/.."
PROTOS_DIR="$ROOT_DIR/protobuf"
PYTHON_OUT_DIR="$ROOT_DIR/python/ccfake"

build_protos() {
    echo "Building ${#@} protobufs"
    for path in "$@"
    do
        echo " -- Building $path"

        python -m grpc_tools.protoc \
            -I ${PROTOS_DIR} \
            --python_out ${PYTHON_OUT_DIR} \
            --grpc_python_out ${PYTHON_OUT_DIR} \
            $path
    done
}

build_protos ${PROTOS_DIR}/*.proto