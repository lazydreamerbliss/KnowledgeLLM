import * as grpc from '@grpc/grpc-js';

import { GrpcServerClient } from './grpc/backend_grpc_pb';
import { BooleanObj } from './grpc/obj_basic_pb';
import { ListOfLibInfoObj } from './grpc/obj_shared_pb';


let client: GrpcServerClient = new GrpcServerClient('http://localhost:8080', grpc.credentials.createInsecure());


