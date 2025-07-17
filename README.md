# pyjetbra - Fully Automated Activator/Keygen/Custom License Tool for JetBrains All Products Pack

[简体中文](./README_zh.md)

> **If this project is helpful to you, please give it a Star to show your support, thank you! 🌟**

> **For learning and research purposes only, please support genuine software!**

## Project Introduction

This project is a fully automated, interactive, and completely customizable tool for generating JetBrains Licenses and `power.conf` files. It supports one-click generation of the License and `power.conf`, and automatically installs them into the `JetBrains/ja-netfilter` environment. **The list of all products is dynamically retrieved in real-time from the official JetBrains API, supporting all products including IDEs, Packs, and plugins.**

- Main Language: Python 3
- License: Apache-2.0
- Repository: https://github.com/TianmuTNT/pyjetbra

## Main Features

- ✅ **Fully Automated CLI**: A beautiful and interactive command-line interface that is easy to operate.
- ✅ **Fully Customizable**: All license information (licensee name, email, expiration date, ID, etc.) can be customized.
- ✅ **Dynamic Product Fetching**: All activatable products are fetched in real-time from the official JetBrains API, supporting IDEs, Packs, plugins, etc.
- ✅ **Multi-select/Select All**: Supports selecting multiple products or all products with a single click.
- ✅ **One-Click Generation**: Automatically generates License and `power.conf`.
- ✅ **Automatic Installation**: Automatically copies `power.conf` and configures environment variables (Windows/Linux/macOS).
- ✅ **Auto-copy License**: Automatically copies the generated license to the clipboard.
- ✅ **ja-netfilter Compatible**: Works in conjunction with the ja-netfilter power plugin.
- ✅ **Clear Code Structure**: Easy for secondary development and contributions.

## How to Use

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the CLI Tool

```bash
python jetbrains_cli.py
```

### 3. Interactive Flow

1.  **Select the products to activate** (supports multi-select/select all, all products are from the official JetBrains API).
2.  **Customize license information** (licensee name, email, expiration date, ID, restriction notes, etc., are all customizable).
3.  **Choose the output directory, whether to regenerate certificates, and whether to display detailed information.**
4.  **Automatically generates License and `power.conf`.**
5.  **Optional: Automatically install into the `JetBrains/ja-netfilter` environment** (automatically copies `power.conf` and configures environment variables).
6.  **The license is automatically copied to the clipboard** for direct activation.

### 4. Generated Files

- `out/certificates/ca.crt` - Certificate file
- `out/certificates/ca.key` - Private key file
- `out/power.conf` - power plugin configuration
- `out/license.txt` - license activation code

## Full Customization Features Explained

- **Product Selection**: All products are fetched in real-time from the official JetBrains API, supporting all products including IDEs, Packs, and plugins. Supports multi-select/select all.
- **License Information**: All fields such as licensee name, assignee, email, expiration date, ID, and restriction notes are fully customizable.
- **Output Directory**: You can customize the save path for the generated files.
- **Certificate Generation**: You can choose whether to regenerate the certificates.
- **Automatic Installation**: Optional automatic installation, which configures `power.conf` and environment variables automatically.

## Platform Support and Notes

- **This tool has only been tested and works well on Windows 10/11.**
- **The code includes automatic adaptation for Linux/macOS, but it has not been actually tested and may not work correctly in many cases.**
- **If you encounter problems on Linux/macOS, you are welcome to submit an issue or a PR to contribute improvements!**

## Disclaimer

- This project is intended for learning, research, and technical exchange purposes only. Do not use it for any commercial or illegal purposes.
- Please support genuine software and respect intellectual property rights!
- The author is not responsible for any consequences arising from the use of this project.

## Contributing

- Contributions via issues and PRs are welcome to improve Linux/macOS support and optimize the user experience.
- The code structure is clear and easy for secondary development.

## License

This project is licensed under the [Apache-2.0 License](./LICENSE).

[![Star History Chart](https://api.star-history.com/svg?repos=TianmuTNT/pyjetbra&type=Date)](https://www.star-history.com/#TianmuTNT/pyjetbra&Date)