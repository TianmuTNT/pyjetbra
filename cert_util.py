#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class CertUtil:
    """证书工具类，用于生成RSA证书和私钥"""
    
    @staticmethod
    def gen_cert(cert_path: str, key_path: str):
        """
        生成RSA证书和私钥
        
        Args:
            cert_path: 证书文件路径
            key_path: 私钥文件路径
        """
        # 生成RSA密钥对
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # 构建证书主题名称
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "Jetbrains"),
        ])
        
        # 构建证书颁发者名称（JetProfile CA 名字不能变，ide内部有检验这个名字是否是JetProfile CA）
        issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "JetProfile CA"),
        ])
        
        # 证书序列号
        serial_number = x509.random_serial_number()
        
        # 证书有效期
        now = datetime.utcnow()
        not_valid_before = now - timedelta(days=365)
        not_valid_after = now + timedelta(days=3650)  # 10年
        
        # 构建证书
        certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            public_key
        ).serial_number(
            serial_number
        ).not_valid_before(
            not_valid_before
        ).not_valid_after(
            not_valid_after
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # 保存证书到PEM文件
        with open(cert_path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))
        
        # 保存私钥到PEM文件
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"证书已生成: {cert_path}")
        print(f"私钥已生成: {key_path}") 