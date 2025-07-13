#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from pem_util import PemUtil


class CodeUtil:
    """激活码工具类，用于生成JetBrains激活码"""
    
    @staticmethod
    def gen_active_code(cert_file: str, key_file: str, license_json_str: str) -> str:
        """
        生成激活码
        
        Args:
            cert_file: 证书文件路径
            key_file: 私钥文件路径
            license_json_str: 许可证JSON字符串
            
        Returns:
            激活码字符串
        """
        # 读取证书和私钥
        cert_bytes = PemUtil.read_pem(cert_file)
        cert_full_str = PemUtil.read_pem_full_str(cert_file)
        cert_str = base64.b64encode(cert_bytes).decode('utf-8')
        
        # 加载私钥
        private_key = PemUtil.load_private_key(key_file)
        
        # 解析许可证JSON
        license_obj = json.loads(license_json_str)
        license_id = license_obj["licenseId"]
        license_bytes = license_json_str.encode('utf-8')
        
        # 使用私钥签名许可证数据
        signature = private_key.sign(
            license_bytes,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        
        # 验证签名（使用证书的公钥）
        certificate = PemUtil.load_certificate(cert_file)
        public_key = certificate.public_key()
        
        try:
            public_key.verify(
                signature,
                license_bytes,
                padding.PKCS1v15(),
                hashes.SHA1()
            )
        except Exception as e:
            raise RuntimeError(f"签名验证失败: {e}")
        
        # 构建激活码
        license_b64 = base64.b64encode(license_bytes).decode('utf-8')
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return f"{license_id}-{license_b64}-{signature_b64}-{cert_str}" 