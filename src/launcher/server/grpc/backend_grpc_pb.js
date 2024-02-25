// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('@grpc/grpc-js');
var obj_basic_pb = require('./obj_basic_pb.js');
var obj_shared_pb = require('./obj_shared_pb.js');

function serialize_BooleanObj(arg) {
  if (!(arg instanceof obj_basic_pb.BooleanObj)) {
    throw new Error('Expected argument of type BooleanObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_BooleanObj(buffer_arg) {
  return obj_basic_pb.BooleanObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_DocLibQueryObj(arg) {
  if (!(arg instanceof obj_shared_pb.DocLibQueryObj)) {
    throw new Error('Expected argument of type DocLibQueryObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_DocLibQueryObj(buffer_arg) {
  return obj_shared_pb.DocLibQueryObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_ImageLibQueryObj(arg) {
  if (!(arg instanceof obj_shared_pb.ImageLibQueryObj)) {
    throw new Error('Expected argument of type ImageLibQueryObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_ImageLibQueryObj(buffer_arg) {
  return obj_shared_pb.ImageLibQueryObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_LibGetReadyParamObj(arg) {
  if (!(arg instanceof obj_shared_pb.LibGetReadyParamObj)) {
    throw new Error('Expected argument of type LibGetReadyParamObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_LibGetReadyParamObj(buffer_arg) {
  return obj_shared_pb.LibGetReadyParamObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_LibInfoObj(arg) {
  if (!(arg instanceof obj_shared_pb.LibInfoObj)) {
    throw new Error('Expected argument of type LibInfoObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_LibInfoObj(buffer_arg) {
  return obj_shared_pb.LibInfoObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_ListOfDocLibQueryResponseObj(arg) {
  if (!(arg instanceof obj_shared_pb.ListOfDocLibQueryResponseObj)) {
    throw new Error('Expected argument of type ListOfDocLibQueryResponseObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_ListOfDocLibQueryResponseObj(buffer_arg) {
  return obj_shared_pb.ListOfDocLibQueryResponseObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_ListOfImageLibQueryResponseObj(arg) {
  if (!(arg instanceof obj_shared_pb.ListOfImageLibQueryResponseObj)) {
    throw new Error('Expected argument of type ListOfImageLibQueryResponseObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_ListOfImageLibQueryResponseObj(buffer_arg) {
  return obj_shared_pb.ListOfImageLibQueryResponseObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_ListOfImageTagObj(arg) {
  if (!(arg instanceof obj_shared_pb.ListOfImageTagObj)) {
    throw new Error('Expected argument of type ListOfImageTagObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_ListOfImageTagObj(buffer_arg) {
  return obj_shared_pb.ListOfImageTagObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_ListOfLibInfoObj(arg) {
  if (!(arg instanceof obj_shared_pb.ListOfLibInfoObj)) {
    throw new Error('Expected argument of type ListOfLibInfoObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_ListOfLibInfoObj(buffer_arg) {
  return obj_shared_pb.ListOfLibInfoObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_ListOfStringObj(arg) {
  if (!(arg instanceof obj_basic_pb.ListOfStringObj)) {
    throw new Error('Expected argument of type ListOfStringObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_ListOfStringObj(buffer_arg) {
  return obj_basic_pb.ListOfStringObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_StringObj(arg) {
  if (!(arg instanceof obj_basic_pb.StringObj)) {
    throw new Error('Expected argument of type StringObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_StringObj(buffer_arg) {
  return obj_basic_pb.StringObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_TaskInfoObj(arg) {
  if (!(arg instanceof obj_shared_pb.TaskInfoObj)) {
    throw new Error('Expected argument of type TaskInfoObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_TaskInfoObj(buffer_arg) {
  return obj_shared_pb.TaskInfoObj.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_VoidObj(arg) {
  if (!(arg instanceof obj_basic_pb.VoidObj)) {
    throw new Error('Expected argument of type VoidObj');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_VoidObj(buffer_arg) {
  return obj_basic_pb.VoidObj.deserializeBinary(new Uint8Array(buffer_arg));
}


// Server APIs
var GrpcServerService = exports.GrpcServerService = {
  // Heartbeat API
heartbeat: {
    path: '/GrpcServer/heartbeat',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.VoidObj,
    responseType: obj_basic_pb.BooleanObj,
    requestSerialize: serialize_VoidObj,
    requestDeserialize: deserialize_VoidObj,
    responseSerialize: serialize_BooleanObj,
    responseDeserialize: deserialize_BooleanObj,
  },
  // Task APIs
get_task_state: {
    path: '/GrpcServer/get_task_state',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.StringObj,
    responseType: obj_shared_pb.TaskInfoObj,
    requestSerialize: serialize_StringObj,
    requestDeserialize: deserialize_StringObj,
    responseSerialize: serialize_TaskInfoObj,
    responseDeserialize: deserialize_TaskInfoObj,
  },
  is_task_done: {
    path: '/GrpcServer/is_task_done',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.StringObj,
    responseType: obj_basic_pb.BooleanObj,
    requestSerialize: serialize_StringObj,
    requestDeserialize: deserialize_StringObj,
    responseSerialize: serialize_BooleanObj,
    responseDeserialize: deserialize_BooleanObj,
  },
  is_task_successful: {
    path: '/GrpcServer/is_task_successful',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.StringObj,
    responseType: obj_basic_pb.BooleanObj,
    requestSerialize: serialize_StringObj,
    requestDeserialize: deserialize_StringObj,
    responseSerialize: serialize_BooleanObj,
    responseDeserialize: deserialize_BooleanObj,
  },
  cancel_task: {
    path: '/GrpcServer/cancel_task',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.StringObj,
    responseType: obj_basic_pb.BooleanObj,
    requestSerialize: serialize_StringObj,
    requestDeserialize: deserialize_StringObj,
    responseSerialize: serialize_BooleanObj,
    responseDeserialize: deserialize_BooleanObj,
  },
  // Library manager APIs for library control
create_library: {
    path: '/GrpcServer/create_library',
    requestStream: false,
    responseStream: false,
    requestType: obj_shared_pb.LibInfoObj,
    responseType: obj_basic_pb.BooleanObj,
    requestSerialize: serialize_LibInfoObj,
    requestDeserialize: deserialize_LibInfoObj,
    responseSerialize: serialize_BooleanObj,
    responseDeserialize: deserialize_BooleanObj,
  },
  use_library: {
    path: '/GrpcServer/use_library',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.StringObj,
    responseType: obj_basic_pb.BooleanObj,
    requestSerialize: serialize_StringObj,
    requestDeserialize: deserialize_StringObj,
    responseSerialize: serialize_BooleanObj,
    responseDeserialize: deserialize_BooleanObj,
  },
  demolish_library: {
    path: '/GrpcServer/demolish_library',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.VoidObj,
    responseType: obj_basic_pb.BooleanObj,
    requestSerialize: serialize_VoidObj,
    requestDeserialize: deserialize_VoidObj,
    responseSerialize: serialize_BooleanObj,
    responseDeserialize: deserialize_BooleanObj,
  },
  get_current_lib_info: {
    path: '/GrpcServer/get_current_lib_info',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.VoidObj,
    responseType: obj_shared_pb.LibInfoObj,
    requestSerialize: serialize_VoidObj,
    requestDeserialize: deserialize_VoidObj,
    responseSerialize: serialize_LibInfoObj,
    responseDeserialize: deserialize_LibInfoObj,
  },
  get_library_list: {
    path: '/GrpcServer/get_library_list',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.VoidObj,
    responseType: obj_shared_pb.ListOfLibInfoObj,
    requestSerialize: serialize_VoidObj,
    requestDeserialize: deserialize_VoidObj,
    responseSerialize: serialize_ListOfLibInfoObj,
    responseDeserialize: deserialize_ListOfLibInfoObj,
  },
  get_library_path_list: {
    path: '/GrpcServer/get_library_path_list',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.VoidObj,
    responseType: obj_basic_pb.ListOfStringObj,
    requestSerialize: serialize_VoidObj,
    requestDeserialize: deserialize_VoidObj,
    responseSerialize: serialize_ListOfStringObj,
    responseDeserialize: deserialize_ListOfStringObj,
  },
  lib_exists: {
    path: '/GrpcServer/lib_exists',
    requestStream: false,
    responseStream: false,
    requestType: obj_basic_pb.StringObj,
    responseType: obj_basic_pb.BooleanObj,
    requestSerialize: serialize_StringObj,
    requestDeserialize: deserialize_StringObj,
    responseSerialize: serialize_BooleanObj,
    responseDeserialize: deserialize_BooleanObj,
  },
  // Document library APIs
make_document_ready: {
    path: '/GrpcServer/make_document_ready',
    requestStream: false,
    responseStream: false,
    requestType: obj_shared_pb.LibGetReadyParamObj,
    responseType: obj_basic_pb.StringObj,
    requestSerialize: serialize_LibGetReadyParamObj,
    requestDeserialize: deserialize_LibGetReadyParamObj,
    responseSerialize: serialize_StringObj,
    responseDeserialize: deserialize_StringObj,
  },
  query_text: {
    path: '/GrpcServer/query_text',
    requestStream: false,
    responseStream: false,
    requestType: obj_shared_pb.DocLibQueryObj,
    responseType: obj_shared_pb.ListOfDocLibQueryResponseObj,
    requestSerialize: serialize_DocLibQueryObj,
    requestDeserialize: deserialize_DocLibQueryObj,
    responseSerialize: serialize_ListOfDocLibQueryResponseObj,
    responseDeserialize: deserialize_ListOfDocLibQueryResponseObj,
  },
  // Image library APIs
scan: {
    path: '/GrpcServer/scan',
    requestStream: false,
    responseStream: false,
    requestType: obj_shared_pb.LibGetReadyParamObj,
    responseType: obj_basic_pb.StringObj,
    requestSerialize: serialize_LibGetReadyParamObj,
    requestDeserialize: deserialize_LibGetReadyParamObj,
    responseSerialize: serialize_StringObj,
    responseDeserialize: deserialize_StringObj,
  },
  image_for_image_search: {
    path: '/GrpcServer/image_for_image_search',
    requestStream: false,
    responseStream: false,
    requestType: obj_shared_pb.ImageLibQueryObj,
    responseType: obj_shared_pb.ListOfImageLibQueryResponseObj,
    requestSerialize: serialize_ImageLibQueryObj,
    requestDeserialize: deserialize_ImageLibQueryObj,
    responseSerialize: serialize_ListOfImageLibQueryResponseObj,
    responseDeserialize: deserialize_ListOfImageLibQueryResponseObj,
  },
  text_for_image_search: {
    path: '/GrpcServer/text_for_image_search',
    requestStream: false,
    responseStream: false,
    requestType: obj_shared_pb.ImageLibQueryObj,
    responseType: obj_shared_pb.ListOfImageLibQueryResponseObj,
    requestSerialize: serialize_ImageLibQueryObj,
    requestDeserialize: deserialize_ImageLibQueryObj,
    responseSerialize: serialize_ListOfImageLibQueryResponseObj,
    responseDeserialize: deserialize_ListOfImageLibQueryResponseObj,
  },
  get_image_tags: {
    path: '/GrpcServer/get_image_tags',
    requestStream: false,
    responseStream: false,
    requestType: obj_shared_pb.ImageLibQueryObj,
    responseType: obj_shared_pb.ListOfImageTagObj,
    requestSerialize: serialize_ImageLibQueryObj,
    requestDeserialize: deserialize_ImageLibQueryObj,
    responseSerialize: serialize_ListOfImageTagObj,
    responseDeserialize: deserialize_ListOfImageTagObj,
  },
};

exports.GrpcServerClient = grpc.makeGenericClientConstructor(GrpcServerService);
