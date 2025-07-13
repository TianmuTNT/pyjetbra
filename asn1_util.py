#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ASN1Util:
    """ASN.1编码工具类"""
    
    # ASN.1标签
    TAG_SEQUENCE = 0x30
    TAG_OCTET_STRING = 0x04
    TAG_OBJECT_IDENTIFIER = 0x06
    TAG_NULL = 0x05
    
    @staticmethod
    def encode_sequence(*elements: bytes) -> bytes:
        """
        编码SEQUENCE
        
        Args:
            *elements: 序列中的元素
            
        Returns:
            编码后的字节序列
        """
        content = b''.join(elements)
        return ASN1Util._encode_tag(ASN1Util.TAG_SEQUENCE, content)
    
    @staticmethod
    def encode_octet_string(data: bytes) -> bytes:
        """
        编码OCTET STRING
        
        Args:
            data: 要编码的数据
            
        Returns:
            编码后的字节序列
        """
        return ASN1Util._encode_tag(ASN1Util.TAG_OCTET_STRING, data)
    
    @staticmethod
    def encode_object_identifier(oid: str) -> bytes:
        """
        编码OBJECT IDENTIFIER
        
        Args:
            oid: OID字符串，如"2.16.840.1.101.3.4.2.1"
            
        Returns:
            编码后的字节序列
        """
        # 解析OID
        parts = [int(x) for x in oid.split('.')]
        
        # 编码OID
        encoded = bytearray()
        for i, part in enumerate(parts):
            if i == 0:
                # 前两个数字编码为 40 * first + second
                if len(parts) < 2:
                    raise ValueError("OID至少需要两个数字")
                encoded.append(40 * parts[0] + parts[1])
                continue
            elif i == 1:
                continue  # 第二个数字已经在上面处理了
            
            # 编码其他数字
            ASN1Util._encode_base128(encoded, part)
        
        return ASN1Util._encode_tag(ASN1Util.TAG_OBJECT_IDENTIFIER, bytes(encoded))
    
    @staticmethod
    def encode_null() -> bytes:
        """
        编码NULL
        
        Returns:
            编码后的字节序列
        """
        return ASN1Util._encode_tag(ASN1Util.TAG_NULL, b'')
    
    @staticmethod
    def _encode_base128(encoded: bytearray, value: int):
        """
        编码base128数字
        
        Args:
            encoded: 编码缓冲区
            value: 要编码的值
        """
        if value == 0:
            encoded.append(0)
            return
        
        # 计算需要的字节数
        temp = value
        byte_count = 0
        while temp > 0:
            temp >>= 7
            byte_count += 1
        
        # 编码
        for i in range(byte_count - 1, -1, -1):
            byte_val = (value >> (7 * i)) & 0x7F
            if i > 0:
                byte_val |= 0x80
            encoded.append(byte_val)
    
    @staticmethod
    def _encode_tag(tag: int, content: bytes) -> bytes:
        """
        编码带标签的内容
        
        Args:
            tag: 标签值
            content: 内容
            
        Returns:
            编码后的字节序列
        """
        length = len(content)
        
        if length < 128:
            # 短长度形式
            return bytes([tag, length]) + content
        else:
            # 长长度形式
            length_bytes = ASN1Util._encode_length(length)
            return bytes([tag]) + length_bytes + content
    
    @staticmethod
    def _encode_length(length: int) -> bytes:
        """
        编码长度
        
        Args:
            length: 长度值
            
        Returns:
            编码后的长度字节
        """
        if length < 128:
            return bytes([length])
        
        # 长长度形式
        length_bytes = []
        while length > 0:
            length_bytes.insert(0, length & 0xFF)
            length >>= 8
        
        # 设置最高位表示长长度形式
        length_bytes[0] |= 0x80
        
        return bytes([0x80 | len(length_bytes)]) + bytes(length_bytes) 