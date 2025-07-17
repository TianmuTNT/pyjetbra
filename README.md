# pyjetbra - JetBrains License/PowerConf Auto Generator

[简体中文](./README_zh.md)

> **If you find this project useful, please give it a Star! Thank you! 🌟**

> **For learning and research only. Please support genuine software!**

## Introduction

pyjetbra is a fully automated, interactive, and highly customizable tool for generating JetBrains licenses and power.conf files. It supports one-click generation of certificates, licenses, and power.conf, and can automatically install them into JetBrains/ja-netfilter environments. **All product lists are dynamically fetched from the JetBrains official API, supporting all IDEs, Packs, Plugins, etc.**

- Language: Python 3
- License: Apache-2.0
- Repository: https://github.com/TianmuTNT/pyjetbra

## Features

- ✅ **Fully automated CLI**: Beautiful interactive command-line interface, easy to use
- ✅ **Fully customizable**: All license fields (owner, email, expiry, ID, etc.) are customizable
- ✅ **Dynamic product list**: All activatable products are fetched from JetBrains official API, including IDEs, Packs, Plugins, etc.
- ✅ **Multi-select/Select all**: Support for multi-select or select all products
- ✅ **One-click generation**: Automatically generates certificate, license, and power.conf
- ✅ **Auto install**: Automatically copies power.conf and configures environment variables (Windows/Linux/macOS)
- ✅ **Auto copy license**: License is automatically copied to clipboard after generation
- ✅ **Compatible with ja-netfilter**: Works with ja-netfilter power plugin
- ✅ **Clean code structure**: Easy for secondary development and contributions

## Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the CLI tool

```bash
python jetbrains_cli.py
```

### 3. Interactive workflow

1. **Select products to activate** (multi-select/select all, all products from JetBrains API)
2. **Customize license info** (all fields customizable: owner, email, expiry, ID, restriction, etc.)
3. **Choose output directory, whether to regenerate certificate, and whether to show details**
4. **Auto-generate certificate, license, power.conf**
5. **Optional: Auto-install to JetBrains/ja-netfilter environment** (auto copy power.conf and set env vars)
6. **License is auto-copied to clipboard** for easy activation

### 4. Generated files

- `out/certificates/ca.crt` - Certificate file
- `out/certificates/ca.key` - Private key file
- `out/power.conf` - Power plugin config
- `out/license.txt` - License activation code

## Customization

- **Product selection**: All products are fetched from JetBrains API, including IDEs, Packs, Plugins, etc., with multi-select/select all
- **License info**: All fields (owner, assignee, email, expiry, ID, restriction, etc.) are fully customizable
- **Output directory**: Customizable output path
- **Certificate generation**: Option to regenerate certificate
- **Auto install**: Optionally auto-install and configure power.conf and environment variables

## Platform Support & Notes

- **Tested and works well on Windows 10/11 only.**
- **Linux/macOS code is implemented but NOT tested; it may not work in many cases.**
- **If you encounter issues on Linux/macOS, PRs and contributions are welcome!**

## Disclaimer

- This project is for learning, research, and technical exchange only. Do not use for any commercial or illegal purposes.
- Please support genuine software and respect intellectual property!
- The author is not responsible for any consequences arising from the use of this project.

## Contributing

- Issues and PRs are welcome, especially to improve Linux/macOS support and user experience.
- The codebase is clean and easy to extend.

## License

This project is licensed under the [Apache-2.0 License](./LICENSE).

[![Star History Chart](https://api.star-history.com/svg?repos=TianmuTNT/pyjetbra&type=Date)](https://www.star-history.com/#TianmuTNT/pyjetbra&Date)
