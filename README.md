# pyjetbra - JetBrains全家桶 全自动激活/Keygen/自定义License 工具

> **🎉 如果本项目对你有帮助，请点个 Star 支持一下，谢谢！**

> **仅供学习研究用途，请支持正版软件！**

## 项目简介

本项目是一个全自动、可交互、完全自定义的 JetBrains License 及 power.conf 生成工具。支持一键生成License、power.conf，并自动安装到 JetBrains/ja-netfilter 环境。**所有产品列表均实时从 JetBrains 官方 API 动态获取，支持 IDE、Pack、插件等全部产品。**

## 主要特性

- ✅ **全自动 CLI**：美观的交互式命令行界面，操作简单
- ✅ **完全自定义**：所有许可证信息（持有者、邮箱、过期时间、ID等）均可自定义
- ✅ **产品动态获取**：所有可激活产品均实时从 JetBrains 官方 API 获取，支持 IDE、Pack、插件等
- ✅ **多选/全选**：支持多选产品或一键全选
- ✅ **一键生成**：自动License、power.conf
- ✅ **自动安装**：自动复制 power.conf 并配置环境变量（Windows/Linux/macOS）
- ✅ **兼容 ja-netfilter**：与 ja-netfilter power 插件配合使用

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行 CLI 工具

```bash
python jetbrains_cli.py
```

### 3. 交互流程

1. **选择要激活的产品**（支持多选/全选，所有产品均来自 JetBrains 官方 API）
2. **自定义许可证信息**（持有者、邮箱、过期时间、ID、限制说明等全部可自定义）
3. **选择输出目录、是否重新生成证书、是否显示详细信息**
4. **自动生成License、power.conf**
5. **可选：自动安装到 JetBrains/ja-netfilter 环境**（自动复制 power.conf 并配置环境变量）
6. **License自动复制到剪贴板**，可直接粘贴激活

### 4. 生成文件

- `out/certificates/ca.crt` - 证书文件
- `out/certificates/ca.key` - 私钥文件
- `out/power.conf` - power 插件配置
- `out/license.txt` - license 激活码

## 平台支持与注意事项

- **本工具仅在 Windows 10/11 上测试通过，运行良好。**
- **Linux/macOS 代码已实现自动适配，但未实际测试，很多情况下可能无法正常工作。**
- **如在 Linux/macOS 下遇到问题，欢迎 PR 贡献改进！**

## 免责声明

- 本项目仅供学习、研究、技术交流使用，请勿用于任何商业或非法用途。
- 请支持正版软件，尊重知识产权！
- 使用本项目造成的一切后果与作者无关。

## 贡献

- 欢迎提交 PR 贡献代码，完善 Linux/macOS 支持，优化交互体验。