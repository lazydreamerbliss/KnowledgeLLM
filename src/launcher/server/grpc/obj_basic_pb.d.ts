// package: 
// file: obj_basic.proto

/* tslint:disable */
/* eslint-disable */

import * as jspb from "google-protobuf";

export class VoidObj extends jspb.Message { 

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): VoidObj.AsObject;
    static toObject(includeInstance: boolean, msg: VoidObj): VoidObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: VoidObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): VoidObj;
    static deserializeBinaryFromReader(message: VoidObj, reader: jspb.BinaryReader): VoidObj;
}

export namespace VoidObj {
    export type AsObject = {
    }
}

export class BooleanObj extends jspb.Message { 
    getValue(): boolean;
    setValue(value: boolean): BooleanObj;
    getError(): string;
    setError(value: string): BooleanObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): BooleanObj.AsObject;
    static toObject(includeInstance: boolean, msg: BooleanObj): BooleanObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: BooleanObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): BooleanObj;
    static deserializeBinaryFromReader(message: BooleanObj, reader: jspb.BinaryReader): BooleanObj;
}

export namespace BooleanObj {
    export type AsObject = {
        value: boolean,
        error: string,
    }
}

export class ListOfBooleanObj extends jspb.Message { 
    clearValueList(): void;
    getValueList(): Array<boolean>;
    setValueList(value: Array<boolean>): ListOfBooleanObj;
    addValue(value: boolean, index?: number): boolean;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ListOfBooleanObj.AsObject;
    static toObject(includeInstance: boolean, msg: ListOfBooleanObj): ListOfBooleanObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ListOfBooleanObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ListOfBooleanObj;
    static deserializeBinaryFromReader(message: ListOfBooleanObj, reader: jspb.BinaryReader): ListOfBooleanObj;
}

export namespace ListOfBooleanObj {
    export type AsObject = {
        valueList: Array<boolean>,
    }
}

export class StringObj extends jspb.Message { 
    getValue(): string;
    setValue(value: string): StringObj;
    getError(): string;
    setError(value: string): StringObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): StringObj.AsObject;
    static toObject(includeInstance: boolean, msg: StringObj): StringObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: StringObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): StringObj;
    static deserializeBinaryFromReader(message: StringObj, reader: jspb.BinaryReader): StringObj;
}

export namespace StringObj {
    export type AsObject = {
        value: string,
        error: string,
    }
}

export class ListOfStringObj extends jspb.Message { 
    clearValueList(): void;
    getValueList(): Array<string>;
    setValueList(value: Array<string>): ListOfStringObj;
    addValue(value: string, index?: number): string;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): ListOfStringObj.AsObject;
    static toObject(includeInstance: boolean, msg: ListOfStringObj): ListOfStringObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: ListOfStringObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): ListOfStringObj;
    static deserializeBinaryFromReader(message: ListOfStringObj, reader: jspb.BinaryReader): ListOfStringObj;
}

export namespace ListOfStringObj {
    export type AsObject = {
        valueList: Array<string>,
    }
}

export class IntegerShortObj extends jspb.Message { 
    getValue(): number;
    setValue(value: number): IntegerShortObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): IntegerShortObj.AsObject;
    static toObject(includeInstance: boolean, msg: IntegerShortObj): IntegerShortObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: IntegerShortObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): IntegerShortObj;
    static deserializeBinaryFromReader(message: IntegerShortObj, reader: jspb.BinaryReader): IntegerShortObj;
}

export namespace IntegerShortObj {
    export type AsObject = {
        value: number,
    }
}

export class IntegerLongObj extends jspb.Message { 
    getValue(): number;
    setValue(value: number): IntegerLongObj;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): IntegerLongObj.AsObject;
    static toObject(includeInstance: boolean, msg: IntegerLongObj): IntegerLongObj.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: IntegerLongObj, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): IntegerLongObj;
    static deserializeBinaryFromReader(message: IntegerLongObj, reader: jspb.BinaryReader): IntegerLongObj;
}

export namespace IntegerLongObj {
    export type AsObject = {
        value: number,
    }
}
