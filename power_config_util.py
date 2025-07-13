#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
from pem_util import PemUtil
from asn1_util import ASN1Util


class PowerConfigUtil:
    """Power配置工具类，用于生成power.conf配置文件"""
    
    # JetBrains内置的私钥
    JET_PRIVATE_KEY = "860106576952879101192782278876319243486072481962999610484027161162448933268423045647258145695082284265933019120714643752088997312766689988016808929265129401027490891810902278465065056686129972085119605237470899952751915070244375173428976413406363879128531449407795115913715863867259163957682164040613505040314747660800424242248055421184038777878268502955477482203711835548014501087778959157112423823275878824729132393281517778742463067583320091009916141454657614089600126948087954465055321987012989937065785013284988096504657892738536613208311013047138019418152103262155848541574327484510025594166239784429845180875774012229784878903603491426732347994359380330103328705981064044872334790365894924494923595382470094461546336020961505275530597716457288511366082299255537762891238136381924520749228412559219346777184174219999640906007205260040707839706131662149325151230558316068068139406816080119906833578907759960298749494098180107991752250725928647349597506532778539709852254478061194098069801549845163358315116260915270480057699929968468068015735162890213859113563672040630687357054902747438421559817252127187138838514773245413540030800888215961904267348727206110582505606182944023582459006406137831940959195566364811905585377246353"
    
    @staticmethod
    def gen_power_plugin_config(cert_file: str, base_dir: str):
        """
        生成power插件配置文件
        
        Args:
            cert_file: 证书文件路径
            base_dir: 输出目录
        """
        # 读取证书
        cert_content = PemUtil.read_pem_full_str(cert_file)
        certificate = PemUtil.load_certificate(cert_file)
        
        # 获取公钥信息
        public_key = certificate.public_key()
        exponent = str(public_key.public_numbers().e)
        
        # 获取证书签名
        cert_signature = int.from_bytes(certificate.signature, byteorder='big')
        
        # 编码签名
        encoded_signature = PowerConfigUtil._encode_signature(
            certificate.tbs_certificate_bytes,
            public_key.key_size
        )
        encoded_signature_int = int.from_bytes(encoded_signature, byteorder='big')
        
        # 生成power.conf内容
        power_config = f"[Result]\nEQUAL,{cert_signature},{exponent},{PowerConfigUtil.JET_PRIVATE_KEY}->{encoded_signature_int}"
        
        # 保存配置文件
        output_path = f"{base_dir}/power.conf"
        with open(output_path, 'w') as f:
            f.write(power_config)
        
        print(f"Power配置文件已生成: {output_path}")
    
    @staticmethod
    def _encode_signature(values: bytes, key_size: int) -> bytes:
        """
        编码签名
        
        Args:
            values: 要编码的数据
            key_size: 密钥大小
            
        Returns:
            编码后的签名
        """
        # 计算SHA-256哈希
        message_digest = hashlib.sha256()
        message_digest.update(values)
        hash_bytes = message_digest.digest()
        
        # 构建DER编码的DigestInfo
        # 对于SHA-256，DigestInfo的格式是：
        # SEQUENCE {
        #   SEQUENCE {
        #     OBJECT IDENTIFIER sha256
        #     NULL
        #   }
        #   OCTET STRING hash
        # }
        
        # 构建内层SEQUENCE（算法标识）
        algorithm_oid = ASN1Util.encode_object_identifier("2.16.840.1.101.3.4.2.1")  # SHA-256 OID
        null_value = ASN1Util.encode_null()
        inner_sequence = ASN1Util.encode_sequence(algorithm_oid, null_value)
        
        # 构建OCTET STRING（哈希值）
        octet_string = ASN1Util.encode_octet_string(hash_bytes)
        
        # 构建外层SEQUENCE
        digest_info = ASN1Util.encode_sequence(inner_sequence, octet_string)
        
        # RSA填充（PKCS#1 v1.5）
        block_size = (key_size + 7) // 8
        padded_data = PowerConfigUtil._pkcs1_pad(digest_info, block_size)
        
        return padded_data
    
    @staticmethod
    def _pkcs1_pad(data: bytes, block_size: int) -> bytes:
        """
        PKCS#1 v1.5填充
        
        Args:
            data: 要填充的数据
            block_size: 块大小
            
        Returns:
            填充后的数据
        """
        if len(data) > block_size - 11:
            raise ValueError("数据太长，无法进行PKCS#1填充")
        
        # 填充格式: 0x00 0x01 0xFF... 0x00 data
        padding_length = block_size - len(data) - 3
        padding = b'\xff' * padding_length
        
        return b'\x00\x01' + padding + b'\x00' + data 