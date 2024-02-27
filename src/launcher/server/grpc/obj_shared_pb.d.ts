// package: 
// file: obj_shared.proto

/* tslint:disable */
/* eslint-disable */

import * as jspb from "google-protobuf";
import * as google_protobuf_timestamp_pb from "google-protobuf/google/protobuf/timestamp_pb";

export class LibInfoObj extends jspb.Message { 
    getName(): string;
    setName(value: string): LibInfoObj;
    getUuid(): string;
    setUuid(value: string): LibInfoObj;
    getPath(): string;
    setPath(value: string): LibInfoObj;
    getType(): string;
    setType(value: string): LibInfoObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): LibInfoObj.AsObject;
    static toObject(includeInstance: boolean, msg: LibInfoObj): LibInfoObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: LibInfoObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): LibInfoObj;
    static deserializeBinaryFromReader(message: LibInfoObj, reader: jspb.BinaryReader): LibInfoObj;
}

export namespace LibInfoObj {
    export type AsObject = {
        name: string,
        uuid: string,
        path: string,
        type: string,
    }
}

export class ListOfLibInfoObj extends jspb.Message { 
    clearValueList(): void;
    getValueList(): Array<LibInfoObj>;
    setValueList(value: Array<LibInfoObj>): ListOfLibInfoObj;
    addValue(value?: LibInfoObj, index?: number): LibInfoObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ListOfLibInfoObj.AsObject;
    static toObject(includeInstance: boolean, msg: ListOfLibInfoObj): ListOfLibInfoObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ListOfLibInfoObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ListOfLibInfoObj;
    static deserializeBinaryFromReader(message: ListOfLibInfoObj, reader: jspb.BinaryReader): ListOfLibInfoObj;
}

export namespace ListOfLibInfoObj {
    export type AsObject = {
        valueList: Array<LibInfoObj.AsObject>,
    }
}

export class LibGetReadyParamObj extends jspb.Message { 
    getForceInit(): boolean;
    setForceInit(value: boolean): LibGetReadyParamObj;
    getRelativePath(): string;
    setRelativePath(value: string): LibGetReadyParamObj;
    getProviderType(): string;
    setProviderType(value: string): LibGetReadyParamObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): LibGetReadyParamObj.AsObject;
    static toObject(includeInstance: boolean, msg: LibGetReadyParamObj): LibGetReadyParamObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: LibGetReadyParamObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): LibGetReadyParamObj;
    static deserializeBinaryFromReader(message: LibGetReadyParamObj, reader: jspb.BinaryReader): LibGetReadyParamObj;
}

export namespace LibGetReadyParamObj {
    export type AsObject = {
        forceInit: boolean,
        relativePath: string,
        providerType: string,
    }
}

export class TaskInfoObj extends jspb.Message { 
    getId(): string;
    setId(value: string): TaskInfoObj;
    getState(): string;
    setState(value: string): TaskInfoObj;
    getPhaseCount(): number;
    setPhaseCount(value: number): TaskInfoObj;
    getPhaseName(): string;
    setPhaseName(value: string): TaskInfoObj;
    getCurrentPhase(): number;
    setCurrentPhase(value: number): TaskInfoObj;
    getProgress(): number;
    setProgress(value: number): TaskInfoObj;
    getError(): string;
    setError(value: string): TaskInfoObj;

    hasSubmittedOn(): boolean;
    clearSubmittedOn(): void;
    getSubmittedOn(): google_protobuf_timestamp_pb.Timestamp | undefined;
    setSubmittedOn(value?: google_protobuf_timestamp_pb.Timestamp): TaskInfoObj;

    hasCompletedOn(): boolean;
    clearCompletedOn(): void;
    getCompletedOn(): google_protobuf_timestamp_pb.Timestamp | undefined;
    setCompletedOn(value?: google_protobuf_timestamp_pb.Timestamp): TaskInfoObj;
    getDuration(): number;
    setDuration(value: number): TaskInfoObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): TaskInfoObj.AsObject;
    static toObject(includeInstance: boolean, msg: TaskInfoObj): TaskInfoObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: TaskInfoObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): TaskInfoObj;
    static deserializeBinaryFromReader(message: TaskInfoObj, reader: jspb.BinaryReader): TaskInfoObj;
}

export namespace TaskInfoObj {
    export type AsObject = {
        id: string,
        state: string,
        phaseCount: number,
        phaseName: string,
        currentPhase: number,
        progress: number,
        error: string,
        submittedOn?: google_protobuf_timestamp_pb.Timestamp.AsObject,
        completedOn?: google_protobuf_timestamp_pb.Timestamp.AsObject,
        duration: number,
    }
}

export class DocLibQueryObj extends jspb.Message { 
    getText(): string;
    setText(value: string): DocLibQueryObj;
    getTopK(): number;
    setTopK(value: number): DocLibQueryObj;
    getRerank(): boolean;
    setRerank(value: boolean): DocLibQueryObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): DocLibQueryObj.AsObject;
    static toObject(includeInstance: boolean, msg: DocLibQueryObj): DocLibQueryObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: DocLibQueryObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): DocLibQueryObj;
    static deserializeBinaryFromReader(message: DocLibQueryObj, reader: jspb.BinaryReader): DocLibQueryObj;
}

export namespace DocLibQueryObj {
    export type AsObject = {
        text: string,
        topK: number,
        rerank: boolean,
    }
}

export class DocLibQueryResponseObj extends jspb.Message { 

    hasTimestamp(): boolean;
    clearTimestamp(): void;
    getTimestamp(): google_protobuf_timestamp_pb.Timestamp | undefined;
    setTimestamp(value?: google_protobuf_timestamp_pb.Timestamp): DocLibQueryResponseObj;
    getText(): string;
    setText(value: string): DocLibQueryResponseObj;
    getSender(): string;
    setSender(value: string): DocLibQueryResponseObj;
    getMessage(): string;
    setMessage(value: string): DocLibQueryResponseObj;
    getReplyTo(): string;
    setReplyTo(value: string): DocLibQueryResponseObj;
    getRepliedMessage(): string;
    setRepliedMessage(value: string): DocLibQueryResponseObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): DocLibQueryResponseObj.AsObject;
    static toObject(includeInstance: boolean, msg: DocLibQueryResponseObj): DocLibQueryResponseObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: DocLibQueryResponseObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): DocLibQueryResponseObj;
    static deserializeBinaryFromReader(message: DocLibQueryResponseObj, reader: jspb.BinaryReader): DocLibQueryResponseObj;
}

export namespace DocLibQueryResponseObj {
    export type AsObject = {
        timestamp?: google_protobuf_timestamp_pb.Timestamp.AsObject,
        text: string,
        sender: string,
        message: string,
        replyTo: string,
        repliedMessage: string,
    }
}

export class ListOfDocLibQueryResponseObj extends jspb.Message { 
    clearValueList(): void;
    getValueList(): Array<DocLibQueryResponseObj>;
    setValueList(value: Array<DocLibQueryResponseObj>): ListOfDocLibQueryResponseObj;
    addValue(value?: DocLibQueryResponseObj, index?: number): DocLibQueryResponseObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ListOfDocLibQueryResponseObj.AsObject;
    static toObject(includeInstance: boolean, msg: ListOfDocLibQueryResponseObj): ListOfDocLibQueryResponseObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ListOfDocLibQueryResponseObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ListOfDocLibQueryResponseObj;
    static deserializeBinaryFromReader(message: ListOfDocLibQueryResponseObj, reader: jspb.BinaryReader): ListOfDocLibQueryResponseObj;
}

export namespace ListOfDocLibQueryResponseObj {
    export type AsObject = {
        valueList: Array<DocLibQueryResponseObj.AsObject>,
    }
}

export class ImageLibQueryObj extends jspb.Message { 
    getImageData(): string;
    setImageData(value: string): ImageLibQueryObj;
    getTopK(): number;
    setTopK(value: number): ImageLibQueryObj;
    getText(): string;
    setText(value: string): ImageLibQueryObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ImageLibQueryObj.AsObject;
    static toObject(includeInstance: boolean, msg: ImageLibQueryObj): ImageLibQueryObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ImageLibQueryObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ImageLibQueryObj;
    static deserializeBinaryFromReader(message: ImageLibQueryObj, reader: jspb.BinaryReader): ImageLibQueryObj;
}

export namespace ImageLibQueryObj {
    export type AsObject = {
        imageData: string,
        topK: number,
        text: string,
    }
}

export class ImageLibQueryResponseObj extends jspb.Message { 
    getUuid(): string;
    setUuid(value: string): ImageLibQueryResponseObj;
    getPath(): string;
    setPath(value: string): ImageLibQueryResponseObj;
    getFilename(): string;
    setFilename(value: string): ImageLibQueryResponseObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ImageLibQueryResponseObj.AsObject;
    static toObject(includeInstance: boolean, msg: ImageLibQueryResponseObj): ImageLibQueryResponseObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ImageLibQueryResponseObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ImageLibQueryResponseObj;
    static deserializeBinaryFromReader(message: ImageLibQueryResponseObj, reader: jspb.BinaryReader): ImageLibQueryResponseObj;
}

export namespace ImageLibQueryResponseObj {
    export type AsObject = {
        uuid: string,
        path: string,
        filename: string,
    }
}

export class ListOfImageLibQueryResponseObj extends jspb.Message { 
    clearValueList(): void;
    getValueList(): Array<ImageLibQueryResponseObj>;
    setValueList(value: Array<ImageLibQueryResponseObj>): ListOfImageLibQueryResponseObj;
    addValue(value?: ImageLibQueryResponseObj, index?: number): ImageLibQueryResponseObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ListOfImageLibQueryResponseObj.AsObject;
    static toObject(includeInstance: boolean, msg: ListOfImageLibQueryResponseObj): ListOfImageLibQueryResponseObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ListOfImageLibQueryResponseObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ListOfImageLibQueryResponseObj;
    static deserializeBinaryFromReader(message: ListOfImageLibQueryResponseObj, reader: jspb.BinaryReader): ListOfImageLibQueryResponseObj;
}

export namespace ListOfImageLibQueryResponseObj {
    export type AsObject = {
        valueList: Array<ImageLibQueryResponseObj.AsObject>,
    }
}

export class ImageTagObj extends jspb.Message { 
    getTag(): string;
    setTag(value: string): ImageTagObj;
    getConfidence(): number;
    setConfidence(value: number): ImageTagObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ImageTagObj.AsObject;
    static toObject(includeInstance: boolean, msg: ImageTagObj): ImageTagObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ImageTagObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ImageTagObj;
    static deserializeBinaryFromReader(message: ImageTagObj, reader: jspb.BinaryReader): ImageTagObj;
}

export namespace ImageTagObj {
    export type AsObject = {
        tag: string,
        confidence: number,
    }
}

export class ListOfImageTagObj extends jspb.Message { 
    clearValueList(): void;
    getValueList(): Array<ImageTagObj>;
    setValueList(value: Array<ImageTagObj>): ListOfImageTagObj;
    addValue(value?: ImageTagObj, index?: number): ImageTagObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ListOfImageTagObj.AsObject;
    static toObject(includeInstance: boolean, msg: ListOfImageTagObj): ListOfImageTagObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ListOfImageTagObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ListOfImageTagObj;
    static deserializeBinaryFromReader(message: ListOfImageTagObj, reader: jspb.BinaryReader): ListOfImageTagObj;
}

export namespace ListOfImageTagObj {
    export type AsObject = {
        valueList: Array<ImageTagObj.AsObject>,
    }
}

export class FileMoveParamObj extends jspb.Message { 
    getRelativePath(): string;
    setRelativePath(value: string): FileMoveParamObj;
    getDestRelativePath(): string;
    setDestRelativePath(value: string): FileMoveParamObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): FileMoveParamObj.AsObject;
    static toObject(includeInstance: boolean, msg: FileMoveParamObj): FileMoveParamObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: FileMoveParamObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): FileMoveParamObj;
    static deserializeBinaryFromReader(message: FileMoveParamObj, reader: jspb.BinaryReader): FileMoveParamObj;
}

export namespace FileMoveParamObj {
    export type AsObject = {
        relativePath: string,
        destRelativePath: string,
    }
}

export class FileRenameParamObj extends jspb.Message { 
    getRelativePath(): string;
    setRelativePath(value: string): FileRenameParamObj;
    getNewName(): string;
    setNewName(value: string): FileRenameParamObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): FileRenameParamObj.AsObject;
    static toObject(includeInstance: boolean, msg: FileRenameParamObj): FileRenameParamObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: FileRenameParamObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): FileRenameParamObj;
    static deserializeBinaryFromReader(message: FileRenameParamObj, reader: jspb.BinaryReader): FileRenameParamObj;
}

export namespace FileRenameParamObj {
    export type AsObject = {
        relativePath: string,
        newName: string,
    }
}

export class FileDeleteParamObj extends jspb.Message { 
    getRelativePath(): string;
    setRelativePath(value: string): FileDeleteParamObj;
    getProviderType(): string;
    setProviderType(value: string): FileDeleteParamObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): FileDeleteParamObj.AsObject;
    static toObject(includeInstance: boolean, msg: FileDeleteParamObj): FileDeleteParamObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: FileDeleteParamObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): FileDeleteParamObj;
    static deserializeBinaryFromReader(message: FileDeleteParamObj, reader: jspb.BinaryReader): FileDeleteParamObj;
}

export namespace FileDeleteParamObj {
    export type AsObject = {
        relativePath: string,
        providerType: string,
    }
}
