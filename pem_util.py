#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import re
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography import x509


class PemUtil:
    """PEM文件工具类，用于读取和保存PEM格式的文件"""
    
    @staticmethod
    def save_to_pem_file(output_path: str, pem_type: str, data: bytes):
        """
        保存数据到PEM文件
        
        Args:
            output_path: 输出文件路径
            pem_type: PEM类型（如CERTIFICATE, PRIVATE KEY等）
            data: 要保存的数据
        """
        pem_content = f"-----BEGIN {pem_type}-----\n"
        pem_content += base64.b64encode(data).decode('utf-8')
        pem_content += f"\n-----END {pem_type}-----\n"
        
        with open(output_path, 'w') as f:
            f.write(pem_content)
    
    @staticmethod
    def read_pem(file_path: str) -> bytes:
        """
        读取PEM文件内容
        
        Args:
            file_path: PEM文件路径
            
        Returns:
            解码后的字节数据
        """
        with open(file_path, 'r') as f:
            content = f.read()
        
        # 提取PEM内容（去除头部和尾部）
        pattern = r'-----BEGIN [^-]+-----\n(.*?)\n-----END [^-]+-----'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            pem_content = match.group(1)
            # 移除所有换行符和空格
            pem_content = ''.join(pem_content.split())
            return base64.b64decode(pem_content)
        else:
            raise ValueError("Invalid PEM file format")
    
    @staticmethod
    def read_pem_full_str(file_path: str) -> str:
        """
        读取PEM文件的完整字符串内容
        
        Args:
            file_path: PEM文件路径
            
        Returns:
            PEM文件的完整字符串内容
        """
        with open(file_path, 'r') as f:
            return f.read()
    
    @staticmethod
    def load_certificate(file_path: str) -> x509.Certificate:
        """
        加载X.509证书
        
        Args:
            file_path: 证书文件路径
            
        Returns:
            X.509证书对象
        """
        with open(file_path, 'rb') as f:
            cert_data = f.read()
        return x509.load_pem_x509_certificate(cert_data)
    
    @staticmethod
    def load_private_key(file_path: str):
        """
        加载私钥
        
        Args:
            file_path: 私钥文件路径
            
        Returns:
            私钥对象
        """
        with open(file_path, 'rb') as f:
            key_data = f.read()
        return load_pem_private_key(key_data, password=None) 