import * as grpc from '@grpc/grpc-js';

import { GrpcServerClient } from './grpc/backend_grpc_pb';
import { BooleanObj } from './grpc/obj_basic_pb';
import { ListOfLibInfoObj } from './grpc/obj_shared_pb';


let client: GrpcServerClient = new GrpcServerClient('http://localhost:8080', grpc.credentials.createInsecure());

// https://dev.to/devaddict/use-grpc-with-node-js-and-typescript-3c58
// https://github.com/badsyntax/grpc-js-typescript/blob/master/examples/grpc_tools_node_protoc_ts/client.ts
