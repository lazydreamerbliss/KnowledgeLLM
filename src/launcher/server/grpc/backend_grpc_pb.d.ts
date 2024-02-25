// package: 
// file: backend.proto

/* tslint:disable */
/* eslint-disable */

import * as grpc from "grpc";
import * as backend_pb from "./backend_pb";
import * as obj_basic_pb from "./obj_basic_pb";
import * as obj_shared_pb from "./obj_shared_pb";

interface IGrpcServerService extends grpc.ServiceDefinition<grpc.UntypedServiceImplementation> {
    heartbeat: IGrpcServerService_Iheartbeat;
    get_task_state: IGrpcServerService_Iget_task_state;
    is_task_done: IGrpcServerService_Iis_task_done;
    is_task_successful: IGrpcServerService_Iis_task_successful;
    cancel_task: IGrpcServerService_Icancel_task;
    create_library: IGrpcServerService_Icreate_library;
    use_library: IGrpcServerService_Iuse_library;
    demolish_library: IGrpcServerService_Idemolish_library;
    get_current_lib_info: IGrpcServerService_Iget_current_lib_info;
    get_library_list: IGrpcServerService_Iget_library_list;
    get_library_path_list: IGrpcServerService_Iget_library_path_list;
    lib_exists: IGrpcServerService_Ilib_exists;
    make_document_ready: IGrpcServerService_Imake_document_ready;
    query_text: IGrpcServerService_Iquery_text;
    scan: IGrpcServerService_Iscan;
    image_for_image_search: IGrpcServerService_Iimage_for_image_search;
    text_for_image_search: IGrpcServerService_Itext_for_image_search;
    get_image_tags: IGrpcServerService_Iget_image_tags;
}

interface IGrpcServerService_Iheartbeat extends grpc.MethodDefinition<obj_basic_pb.VoidObj, obj_basic_pb.BooleanObj> {
    path: "/GrpcServer/heartbeat";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.VoidObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.VoidObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.BooleanObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.BooleanObj>;
}
interface IGrpcServerService_Iget_task_state extends grpc.MethodDefinition<obj_basic_pb.StringObj, obj_shared_pb.TaskInfoObj> {
    path: "/GrpcServer/get_task_state";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.StringObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.StringObj>;
    responseSerialize: grpc.serialize<obj_shared_pb.TaskInfoObj>;
    responseDeserialize: grpc.deserialize<obj_shared_pb.TaskInfoObj>;
}
interface IGrpcServerService_Iis_task_done extends grpc.MethodDefinition<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj> {
    path: "/GrpcServer/is_task_done";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.StringObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.StringObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.BooleanObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.BooleanObj>;
}
interface IGrpcServerService_Iis_task_successful extends grpc.MethodDefinition<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj> {
    path: "/GrpcServer/is_task_successful";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.StringObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.StringObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.BooleanObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.BooleanObj>;
}
interface IGrpcServerService_Icancel_task extends grpc.MethodDefinition<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj> {
    path: "/GrpcServer/cancel_task";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.StringObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.StringObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.BooleanObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.BooleanObj>;
}
interface IGrpcServerService_Icreate_library extends grpc.MethodDefinition<obj_shared_pb.LibInfoObj, obj_basic_pb.BooleanObj> {
    path: "/GrpcServer/create_library";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_shared_pb.LibInfoObj>;
    requestDeserialize: grpc.deserialize<obj_shared_pb.LibInfoObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.BooleanObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.BooleanObj>;
}
interface IGrpcServerService_Iuse_library extends grpc.MethodDefinition<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj> {
    path: "/GrpcServer/use_library";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.StringObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.StringObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.BooleanObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.BooleanObj>;
}
interface IGrpcServerService_Idemolish_library extends grpc.MethodDefinition<obj_basic_pb.VoidObj, obj_basic_pb.BooleanObj> {
    path: "/GrpcServer/demolish_library";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.VoidObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.VoidObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.BooleanObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.BooleanObj>;
}
interface IGrpcServerService_Iget_current_lib_info extends grpc.MethodDefinition<obj_basic_pb.VoidObj, obj_shared_pb.LibInfoObj> {
    path: "/GrpcServer/get_current_lib_info";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.VoidObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.VoidObj>;
    responseSerialize: grpc.serialize<obj_shared_pb.LibInfoObj>;
    responseDeserialize: grpc.deserialize<obj_shared_pb.LibInfoObj>;
}
interface IGrpcServerService_Iget_library_list extends grpc.MethodDefinition<obj_basic_pb.VoidObj, obj_shared_pb.ListOfLibInfoObj> {
    path: "/GrpcServer/get_library_list";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.VoidObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.VoidObj>;
    responseSerialize: grpc.serialize<obj_shared_pb.ListOfLibInfoObj>;
    responseDeserialize: grpc.deserialize<obj_shared_pb.ListOfLibInfoObj>;
}
interface IGrpcServerService_Iget_library_path_list extends grpc.MethodDefinition<obj_basic_pb.VoidObj, obj_basic_pb.ListOfStringObj> {
    path: "/GrpcServer/get_library_path_list";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.VoidObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.VoidObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.ListOfStringObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.ListOfStringObj>;
}
interface IGrpcServerService_Ilib_exists extends grpc.MethodDefinition<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj> {
    path: "/GrpcServer/lib_exists";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_basic_pb.StringObj>;
    requestDeserialize: grpc.deserialize<obj_basic_pb.StringObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.BooleanObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.BooleanObj>;
}
interface IGrpcServerService_Imake_document_ready extends grpc.MethodDefinition<obj_shared_pb.LibGetReadyParamObj, obj_basic_pb.StringObj> {
    path: "/GrpcServer/make_document_ready";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_shared_pb.LibGetReadyParamObj>;
    requestDeserialize: grpc.deserialize<obj_shared_pb.LibGetReadyParamObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.StringObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.StringObj>;
}
interface IGrpcServerService_Iquery_text extends grpc.MethodDefinition<obj_shared_pb.DocLibQueryObj, obj_shared_pb.ListOfDocLibQueryResponseObj> {
    path: "/GrpcServer/query_text";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_shared_pb.DocLibQueryObj>;
    requestDeserialize: grpc.deserialize<obj_shared_pb.DocLibQueryObj>;
    responseSerialize: grpc.serialize<obj_shared_pb.ListOfDocLibQueryResponseObj>;
    responseDeserialize: grpc.deserialize<obj_shared_pb.ListOfDocLibQueryResponseObj>;
}
interface IGrpcServerService_Iscan extends grpc.MethodDefinition<obj_shared_pb.LibGetReadyParamObj, obj_basic_pb.StringObj> {
    path: "/GrpcServer/scan";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_shared_pb.LibGetReadyParamObj>;
    requestDeserialize: grpc.deserialize<obj_shared_pb.LibGetReadyParamObj>;
    responseSerialize: grpc.serialize<obj_basic_pb.StringObj>;
    responseDeserialize: grpc.deserialize<obj_basic_pb.StringObj>;
}
interface IGrpcServerService_Iimage_for_image_search extends grpc.MethodDefinition<obj_shared_pb.ImageLibQueryObj, obj_shared_pb.ListOfImageLibQueryResponseObj> {
    path: "/GrpcServer/image_for_image_search";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_shared_pb.ImageLibQueryObj>;
    requestDeserialize: grpc.deserialize<obj_shared_pb.ImageLibQueryObj>;
    responseSerialize: grpc.serialize<obj_shared_pb.ListOfImageLibQueryResponseObj>;
    responseDeserialize: grpc.deserialize<obj_shared_pb.ListOfImageLibQueryResponseObj>;
}
interface IGrpcServerService_Itext_for_image_search extends grpc.MethodDefinition<obj_shared_pb.ImageLibQueryObj, obj_shared_pb.ListOfImageLibQueryResponseObj> {
    path: "/GrpcServer/text_for_image_search";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_shared_pb.ImageLibQueryObj>;
    requestDeserialize: grpc.deserialize<obj_shared_pb.ImageLibQueryObj>;
    responseSerialize: grpc.serialize<obj_shared_pb.ListOfImageLibQueryResponseObj>;
    responseDeserialize: grpc.deserialize<obj_shared_pb.ListOfImageLibQueryResponseObj>;
}
interface IGrpcServerService_Iget_image_tags extends grpc.MethodDefinition<obj_shared_pb.ImageLibQueryObj, obj_shared_pb.ListOfImageTagObj> {
    path: "/GrpcServer/get_image_tags";
    requestStream: false;
    responseStream: false;
    requestSerialize: grpc.serialize<obj_shared_pb.ImageLibQueryObj>;
    requestDeserialize: grpc.deserialize<obj_shared_pb.ImageLibQueryObj>;
    responseSerialize: grpc.serialize<obj_shared_pb.ListOfImageTagObj>;
    responseDeserialize: grpc.deserialize<obj_shared_pb.ListOfImageTagObj>;
}

export const GrpcServerService: IGrpcServerService;

export interface IGrpcServerServer {
    heartbeat: grpc.handleUnaryCall<obj_basic_pb.VoidObj, obj_basic_pb.BooleanObj>;
    get_task_state: grpc.handleUnaryCall<obj_basic_pb.StringObj, obj_shared_pb.TaskInfoObj>;
    is_task_done: grpc.handleUnaryCall<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj>;
    is_task_successful: grpc.handleUnaryCall<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj>;
    cancel_task: grpc.handleUnaryCall<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj>;
    create_library: grpc.handleUnaryCall<obj_shared_pb.LibInfoObj, obj_basic_pb.BooleanObj>;
    use_library: grpc.handleUnaryCall<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj>;
    demolish_library: grpc.handleUnaryCall<obj_basic_pb.VoidObj, obj_basic_pb.BooleanObj>;
    get_current_lib_info: grpc.handleUnaryCall<obj_basic_pb.VoidObj, obj_shared_pb.LibInfoObj>;
    get_library_list: grpc.handleUnaryCall<obj_basic_pb.VoidObj, obj_shared_pb.ListOfLibInfoObj>;
    get_library_path_list: grpc.handleUnaryCall<obj_basic_pb.VoidObj, obj_basic_pb.ListOfStringObj>;
    lib_exists: grpc.handleUnaryCall<obj_basic_pb.StringObj, obj_basic_pb.BooleanObj>;
    make_document_ready: grpc.handleUnaryCall<obj_shared_pb.LibGetReadyParamObj, obj_basic_pb.StringObj>;
    query_text: grpc.handleUnaryCall<obj_shared_pb.DocLibQueryObj, obj_shared_pb.ListOfDocLibQueryResponseObj>;
    scan: grpc.handleUnaryCall<obj_shared_pb.LibGetReadyParamObj, obj_basic_pb.StringObj>;
    image_for_image_search: grpc.handleUnaryCall<obj_shared_pb.ImageLibQueryObj, obj_shared_pb.ListOfImageLibQueryResponseObj>;
    text_for_image_search: grpc.handleUnaryCall<obj_shared_pb.ImageLibQueryObj, obj_shared_pb.ListOfImageLibQueryResponseObj>;
    get_image_tags: grpc.handleUnaryCall<obj_shared_pb.ImageLibQueryObj, obj_shared_pb.ListOfImageTagObj>;
}

export interface IGrpcServerClient {
    heartbeat(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    heartbeat(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    heartbeat(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    get_task_state(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.TaskInfoObj) => void): grpc.ClientUnaryCall;
    get_task_state(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.TaskInfoObj) => void): grpc.ClientUnaryCall;
    get_task_state(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.TaskInfoObj) => void): grpc.ClientUnaryCall;
    is_task_done(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    is_task_done(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    is_task_done(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    is_task_successful(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    is_task_successful(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    is_task_successful(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    cancel_task(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    cancel_task(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    cancel_task(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    create_library(request: obj_shared_pb.LibInfoObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    create_library(request: obj_shared_pb.LibInfoObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    create_library(request: obj_shared_pb.LibInfoObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    use_library(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    use_library(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    use_library(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    demolish_library(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    demolish_library(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    demolish_library(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    get_current_lib_info(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.LibInfoObj) => void): grpc.ClientUnaryCall;
    get_current_lib_info(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.LibInfoObj) => void): grpc.ClientUnaryCall;
    get_current_lib_info(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.LibInfoObj) => void): grpc.ClientUnaryCall;
    get_library_list(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfLibInfoObj) => void): grpc.ClientUnaryCall;
    get_library_list(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfLibInfoObj) => void): grpc.ClientUnaryCall;
    get_library_list(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfLibInfoObj) => void): grpc.ClientUnaryCall;
    get_library_path_list(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.ListOfStringObj) => void): grpc.ClientUnaryCall;
    get_library_path_list(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.ListOfStringObj) => void): grpc.ClientUnaryCall;
    get_library_path_list(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.ListOfStringObj) => void): grpc.ClientUnaryCall;
    lib_exists(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    lib_exists(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    lib_exists(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    make_document_ready(request: obj_shared_pb.LibGetReadyParamObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    make_document_ready(request: obj_shared_pb.LibGetReadyParamObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    make_document_ready(request: obj_shared_pb.LibGetReadyParamObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    query_text(request: obj_shared_pb.DocLibQueryObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfDocLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    query_text(request: obj_shared_pb.DocLibQueryObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfDocLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    query_text(request: obj_shared_pb.DocLibQueryObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfDocLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    scan(request: obj_shared_pb.LibGetReadyParamObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    scan(request: obj_shared_pb.LibGetReadyParamObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    scan(request: obj_shared_pb.LibGetReadyParamObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    image_for_image_search(request: obj_shared_pb.ImageLibQueryObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    image_for_image_search(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    image_for_image_search(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    text_for_image_search(request: obj_shared_pb.ImageLibQueryObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    text_for_image_search(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    text_for_image_search(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    get_image_tags(request: obj_shared_pb.ImageLibQueryObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageTagObj) => void): grpc.ClientUnaryCall;
    get_image_tags(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageTagObj) => void): grpc.ClientUnaryCall;
    get_image_tags(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageTagObj) => void): grpc.ClientUnaryCall;
}

export class GrpcServerClient extends grpc.Client implements IGrpcServerClient {
    constructor(address: string, credentials: grpc.ChannelCredentials, options?: object);
    public heartbeat(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public heartbeat(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public heartbeat(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public get_task_state(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.TaskInfoObj) => void): grpc.ClientUnaryCall;
    public get_task_state(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.TaskInfoObj) => void): grpc.ClientUnaryCall;
    public get_task_state(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.TaskInfoObj) => void): grpc.ClientUnaryCall;
    public is_task_done(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public is_task_done(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public is_task_done(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public is_task_successful(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public is_task_successful(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public is_task_successful(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public cancel_task(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public cancel_task(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public cancel_task(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public create_library(request: obj_shared_pb.LibInfoObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public create_library(request: obj_shared_pb.LibInfoObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public create_library(request: obj_shared_pb.LibInfoObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public use_library(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public use_library(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public use_library(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public demolish_library(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public demolish_library(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public demolish_library(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public get_current_lib_info(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.LibInfoObj) => void): grpc.ClientUnaryCall;
    public get_current_lib_info(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.LibInfoObj) => void): grpc.ClientUnaryCall;
    public get_current_lib_info(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.LibInfoObj) => void): grpc.ClientUnaryCall;
    public get_library_list(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfLibInfoObj) => void): grpc.ClientUnaryCall;
    public get_library_list(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfLibInfoObj) => void): grpc.ClientUnaryCall;
    public get_library_list(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfLibInfoObj) => void): grpc.ClientUnaryCall;
    public get_library_path_list(request: obj_basic_pb.VoidObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.ListOfStringObj) => void): grpc.ClientUnaryCall;
    public get_library_path_list(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.ListOfStringObj) => void): grpc.ClientUnaryCall;
    public get_library_path_list(request: obj_basic_pb.VoidObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.ListOfStringObj) => void): grpc.ClientUnaryCall;
    public lib_exists(request: obj_basic_pb.StringObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public lib_exists(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public lib_exists(request: obj_basic_pb.StringObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.BooleanObj) => void): grpc.ClientUnaryCall;
    public make_document_ready(request: obj_shared_pb.LibGetReadyParamObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    public make_document_ready(request: obj_shared_pb.LibGetReadyParamObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    public make_document_ready(request: obj_shared_pb.LibGetReadyParamObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    public query_text(request: obj_shared_pb.DocLibQueryObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfDocLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public query_text(request: obj_shared_pb.DocLibQueryObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfDocLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public query_text(request: obj_shared_pb.DocLibQueryObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfDocLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public scan(request: obj_shared_pb.LibGetReadyParamObj, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    public scan(request: obj_shared_pb.LibGetReadyParamObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    public scan(request: obj_shared_pb.LibGetReadyParamObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_basic_pb.StringObj) => void): grpc.ClientUnaryCall;
    public image_for_image_search(request: obj_shared_pb.ImageLibQueryObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public image_for_image_search(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public image_for_image_search(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public text_for_image_search(request: obj_shared_pb.ImageLibQueryObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public text_for_image_search(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public text_for_image_search(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageLibQueryResponseObj) => void): grpc.ClientUnaryCall;
    public get_image_tags(request: obj_shared_pb.ImageLibQueryObj, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageTagObj) => void): grpc.ClientUnaryCall;
    public get_image_tags(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageTagObj) => void): grpc.ClientUnaryCall;
    public get_image_tags(request: obj_shared_pb.ImageLibQueryObj, metadata: grpc.Metadata, options: Partial<grpc.CallOptions>, callback: (error: grpc.ServiceError | null, response: obj_shared_pb.ListOfImageTagObj) => void): grpc.ClientUnaryCall;
}
