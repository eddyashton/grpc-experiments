# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: registry.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eregistry.proto\x12\x06\x63\x63\x66\x61ke\"D\n\x0fRegisterRequest\x12\x16\n\x0e\x65xecutor_ident\x18\x01 \x01(\x0c\x12\x19\n\x11\x64ispatch_category\x18\x02 \x01(\t\"3\n\x10RegisterResponse\x12\x10\n\x08\x61\x63\x63\x65pted\x18\x01 \x01(\x08\x12\r\n\x05\x65rror\x18\x02 \x01(\t2K\n\x08Registry\x12?\n\x08Register\x12\x17.ccfake.RegisterRequest\x1a\x18.ccfake.RegisterResponse\"\x00\x62\x06proto3')



_REGISTERREQUEST = DESCRIPTOR.message_types_by_name['RegisterRequest']
_REGISTERRESPONSE = DESCRIPTOR.message_types_by_name['RegisterResponse']
RegisterRequest = _reflection.GeneratedProtocolMessageType('RegisterRequest', (_message.Message,), {
  'DESCRIPTOR' : _REGISTERREQUEST,
  '__module__' : 'registry_pb2'
  # @@protoc_insertion_point(class_scope:ccfake.RegisterRequest)
  })
_sym_db.RegisterMessage(RegisterRequest)

RegisterResponse = _reflection.GeneratedProtocolMessageType('RegisterResponse', (_message.Message,), {
  'DESCRIPTOR' : _REGISTERRESPONSE,
  '__module__' : 'registry_pb2'
  # @@protoc_insertion_point(class_scope:ccfake.RegisterResponse)
  })
_sym_db.RegisterMessage(RegisterResponse)

_REGISTRY = DESCRIPTOR.services_by_name['Registry']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REGISTERREQUEST._serialized_start=26
  _REGISTERREQUEST._serialized_end=94
  _REGISTERRESPONSE._serialized_start=96
  _REGISTERRESPONSE._serialized_end=147
  _REGISTRY._serialized_start=149
  _REGISTRY._serialized_end=224
# @@protoc_insertion_point(module_scope)