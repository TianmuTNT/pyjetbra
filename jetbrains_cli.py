#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich import box
import requests

from cert_util import CertUtil
from code_util import CodeUtil
from power_config_util import PowerConfigUtil
from jetbrains_env import uninstall_all_users, install_all_users

console = Console()

# 在 JetBrainsCLI 类前添加多语言支持
LANGUAGES = {
    'en': {
        'main_menu': 'Main Menu: Please select an action',
        'generate': 'Generate License and power.conf',
        'install': 'Auto Install to JetBrains',
        'language': 'Language/语言',
        'exit': 'Exit',
        'exit_msg': 'Exited. Goodbye!',
        'select_language': 'Select language',
        'lang_en': 'English',
        'lang_zh': '简体中文',
        'product_step': 'Step 1: Select products to activate (supports IDE, Pack, plugins, etc.)',
        'product_api': 'All products are from JetBrains official API, supports multi-select and select all.',
        'product_table': 'Available JetBrains Products',
        'product_code': 'Code',
        'product_group': 'Type',
        'product_name': 'Name',
        'product_select': 'Please select products to activate (space to select, enter to confirm)',
        'product_all': 'All Products',
        'product_selected': 'Selected {count} products',
        'product_error': 'Error: Please select at least one product',
        'license_step': 'Step 2: Customize license information',
        'license_tip': 'You can customize all license information.',
        'licensee_name': 'Licensee Name',
        'assignee_name': 'Assignee Name',
        'assignee_email': 'Assignee Email',
        'expire_date': 'License Expiry Date (YYYY-MM-DD)',
        'license_restriction': 'License Restriction',
        'license_id': 'License ID',
        'license_set': 'License information set',
        'license_error': 'Error: Failed to set license information',
        'gen_step': 'Step 3: Generation options',
        'output_dir': 'Output directory',
        'regenerate_cert': 'Regenerate certificate (if exists)?',
        'show_license': 'Show generated license content?',
        'gen_license': 'Generating license and config files...',
        'gen_cert': 'Generating RSA certificate and private key...',
        'cert_done': 'Certificate generated',
        'cert_exist': 'Using existing certificate',
        'gen_power': 'Generating power.conf config file...',
        'power_done': 'power.conf generated',
        'gen_license2': 'Generating license...',
        'license_done': 'License generated',
        'gen_code': 'Generating activation code...',
        'code_done': 'Activation code generated',
        'gen_error': 'Error:',
        'gen_success': 'Generation complete!',
        'file_table': 'Generated Files',
        'file': 'File',
        'path': 'Path',
        'desc': 'Description',
        'cert_file': 'Certificate',
        'key_file': 'Private Key',
        'power_file': 'Power Config',
        'license_file': 'License',
        'cert_desc': 'RSA certificate file',
        'key_desc': 'RSA private key file',
        'power_desc': 'Power plugin config',
        'license_desc': 'License file',
        'license_panel': 'License:',
        'license_info': 'License Info:',
        'license_id2': 'License ID',
        'licensee': 'Licensee',
        'assignee': 'Assignee',
        'email': 'Email',
        'expiry': 'Expiry Date',
        'product_count': 'Product Count',
        'usage': 'Usage:',
        'usage1': '1. Copy power.conf to jetbra/config-jetbrains directory',
        'usage2': '2. Use the generated license to activate JetBrains products',
        'usage3': '3. Keep certificate and private key safe',
        'not_found': 'Not found power.conf or license.txt, please generate first!',
        'auto_install': 'Start auto installation...',
        'find_jetbra': 'Found jetbra directory:',
        'copy_power': 'Copying power.conf file...',
        'copy_done': 'power.conf copied',
        'uninstall_env': 'Uninstalling old environment variables...',
        'install_env': 'Installing new environment variables...',
        'copy_clipboard': 'License copied to clipboard',
        'install_done': 'Installation complete!',
        'open_jetbrains': 'Now you can open JetBrains product and paste the license to activate',
        'pyperclip_tip': 'Tip: Install pyperclip to auto copy license to clipboard',
        'license_content': 'License content:',
        'auto_install_fail': 'Auto installation failed:',
        'manual_install': 'Please complete installation manually',
        'find_jetbra_fail': 'Error: jetbra directory not found, please download and extract jetbra.zip',
        'cancel': 'Operation cancelled by user',
        'program_error': 'Program error:',
    },
    'zh': {
        'main_menu': '主菜单：请选择要执行的操作',
        'generate': '生成 License 和 power.conf',
        'install': '自动安装到 JetBrains',
        'language': 'Language/语言',
        'exit': '退出',
        'exit_msg': '已退出程序，再见！',
        'select_language': '请选择语言',
        'lang_en': 'English',
        'lang_zh': '简体中文',
        'product_step': '第一步：选择要激活的产品（支持IDE、Pack、插件等）',
        'product_api': '所有产品均来自JetBrains官方API，支持多选和全选。',
        'product_table': '可用的JetBrains产品',
        'product_code': '代码',
        'product_group': '类型',
        'product_name': '名称',
        'product_select': '请选择要激活的产品（空格选择，回车确认）',
        'product_all': '全部产品',
        'product_selected': '已选择 {count} 个产品',
        'product_error': '错误：请至少选择一个产品',
        'license_step': '第二步：自定义许可证信息',
        'license_tip': '您可以自定义许可证的所有信息。',
        'licensee_name': '许可证持有者名称',
        'assignee_name': '被授权人姓名',
        'assignee_email': '被授权人邮箱',
        'expire_date': '许可证过期日期 (YYYY-MM-DD)',
        'license_restriction': '许可证限制说明',
        'license_id': '许可证ID',
        'license_set': '许可证信息已设置',
        'license_error': '错误：许可证信息设置失败',
        'gen_step': '第三步：生成选项',
        'output_dir': '输出目录',
        'regenerate_cert': '是否重新生成证书（如果已存在）',
        'show_license': '是否显示生成的许可证内容',
        'gen_license': '正在生成许可证和配置文件...',
        'gen_cert': '生成RSA证书和私钥...',
        'cert_done': '证书生成完成',
        'cert_exist': '使用现有证书',
        'gen_power': '生成power.conf配置文件...',
        'power_done': 'power.conf生成完成',
        'gen_license2': '生成许可证...',
        'license_done': '许可证生成完成',
        'gen_code': '生成激活码...',
        'code_done': '激活码生成完成',
        'gen_error': '错误：',
        'gen_success': '生成完成！',
        'file_table': '生成的文件',
        'file': '文件',
        'path': '路径',
        'desc': '说明',
        'cert_file': '证书',
        'key_file': '私钥',
        'power_file': 'Power配置',
        'license_file': 'License',
        'cert_desc': 'RSA证书文件',
        'key_desc': 'RSA私钥文件',
        'power_desc': 'Power插件配置',
        'license_desc': 'License文件',
        'license_panel': 'License：',
        'license_info': '许可证信息：',
        'license_id2': '许可证ID',
        'licensee': '持有者',
        'assignee': '被授权人',
        'email': '邮箱',
        'expiry': '过期日期',
        'product_count': '产品数量',
        'usage': '使用说明：',
        'usage1': '1. 将 power.conf 文件复制到 jetbra/config-jetbrains 目录',
        'usage2': '2. 使用生成的license激活JetBrains产品',
        'usage3': '3. 证书和私钥文件请妥善保管',
        'not_found': '未找到 power.conf 或 license.txt，请先生成！',
        'auto_install': '开始自动安装...',
        'find_jetbra': '找到jetbra目录：',
        'copy_power': '复制power.conf文件...',
        'copy_done': 'power.conf复制完成',
        'uninstall_env': '正在卸载旧环境变量...',
        'install_env': '正在安装新环境变量...',
        'copy_clipboard': 'License已复制到剪贴板',
        'install_done': '安装完成！',
        'open_jetbrains': '现在可以打开JetBrains产品，粘贴license进行激活',
        'pyperclip_tip': '提示：安装pyperclip可以自动复制license到剪贴板',
        'license_content': 'License内容：',
        'auto_install_fail': '自动安装失败：',
        'manual_install': '请手动完成安装步骤',
        'find_jetbra_fail': '错误：未找到jetbra目录，请确保已下载jetbra.zip并解压',
        'cancel': '用户取消操作',
        'program_error': '程序错误：',
    }
}

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {"language": "en"}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    # 写入默认配置
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

class JetBrainsCLI:
    """JetBrains许可证生成CLI工具"""
    
    API_URL = "https://account.jetbrains.com/services/rest/coupon/v1/redeem/items/personal"
    
    def __init__(self):
        self.selected_products = []
        self.license_info = {}
        self.output_dir = "out"
        self.config = load_config()
        self.language = self.config.get('language', 'en')
        self.L = LANGUAGES[self.language]
    
    def set_language(self, lang):
        self.language = lang
        self.L = LANGUAGES[self.language]
        self.config['language'] = lang
        save_config(self.config)
    
    def show_banner(self):
        """显示欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    JetBrains License Generator               ║
║                       许可证生成工具                         ║
╚══════════════════════════════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold blue", box=box.DOUBLE))
    
    def fetch_all_products(self):
        try:
            resp = requests.get(self.API_URL, timeout=10)
            data = resp.json()
            products = []
            for group in ["products", "packs", "plugins"]:
                for item in data.get(group, []):
                    products.append({
                        "code": item["code"],
                        "name": item["name"],
                        "group": group
                    })
            return products
        except Exception as e:
            console.print(f"[red]获取产品列表失败：{e}，将使用本地内置产品列表[/red]")
            # fallback: 只用原有IDE列表
            return [
                {"code": "II", "name": "IntelliJ IDEA Ultimate", "group": "products"},
                {"code": "CL", "name": "CLion", "group": "products"},
                {"code": "PS", "name": "PhpStorm", "group": "products"},
                {"code": "GO", "name": "GoLand", "group": "products"},
                {"code": "PC", "name": "PyCharm", "group": "products"},
                {"code": "WS", "name": "WebStorm", "group": "products"},
                {"code": "RD", "name": "Rider", "group": "products"},
                {"code": "DB", "name": "DataGrip", "group": "products"},
                {"code": "RM", "name": "RubyMine", "group": "products"},
                {"code": "DS", "name": "DataSpell", "group": "products"},
                {"code": "RR", "name": "RustRover", "group": "products"},
            ]
    
    def show_product_selection(self):
        console.print("\n[bold cyan]第一步：选择要激活的产品（支持IDE、Pack、插件等）[/bold cyan]")
        console.print("所有产品均来自JetBrains官方API，支持多选和全选。\n")
        all_products = self.fetch_all_products()
        # 构建分组展示
        table = Table(title="可用的JetBrains产品", show_header=True, header_style="bold magenta")
        table.add_column("代码", style="cyan", width=10)
        table.add_column("类型", style="yellow", width=10)
        table.add_column("名称", style="green", width=40)
        for item in all_products:
            table.add_row(item["code"], item["group"], item["name"])
        console.print(table)
        # 构建多选菜单
        choices = [(f"[{item['group']}] {item['name']}", item["code"]) for item in all_products]
        questions = [
            inquirer.Checkbox(
                'products',
                message="请选择要激活的产品（空格选择，回车确认）",
                choices=[("全部产品", "ALL")] + choices
            )
        ]
        answers = inquirer.prompt(questions)
        if answers and answers['products']:
            if "ALL" in answers['products']:
                self.selected_products = [item["code"] for item in all_products]
            else:
                self.selected_products = answers['products']
            console.print(f"\n[green]✓ 已选择 {len(self.selected_products)} 个产品[/green]")
        else:
            console.print("\n[red]错误：请至少选择一个产品[/red]")
            return False
        return True
    
    def show_license_customization(self):
        """许可证信息自定义界面"""
        console.print("\n[bold cyan]第二步：自定义许可证信息[/bold cyan]")
        console.print("您可以自定义许可证的所有信息。\n")
        
        # 默认值
        default_licensee_name = "Your Name"
        default_assignee_name = "Your Company"
        default_assignee_email = "your.email@example.com"
        default_expire_date = "2099-12-31"
        default_license_restriction = "Generated by JetBrains License Generator"
        
        # 许可证信息输入
        questions = [
            inquirer.Text(
                'licensee_name',
                message="许可证持有者名称",
                default=default_licensee_name
            ),
            inquirer.Text(
                'assignee_name',
                message="被授权人姓名",
                default=default_assignee_name
            ),
            inquirer.Text(
                'assignee_email',
                message="被授权人邮箱",
                default=default_assignee_email
            ),
            inquirer.Text(
                'expire_date',
                message="许可证过期日期 (YYYY-MM-DD)",
                default=default_expire_date
            ),
            inquirer.Text(
                'license_restriction',
                message="许可证限制说明",
                default=default_license_restriction
            ),
            inquirer.Text(
                'license_id',
                message="许可证ID",
                default="CUSTOM_LICENSE"
            )
        ]
        
        answers = inquirer.prompt(questions)
        if answers:
            self.license_info = answers
            console.print(f"\n[green]✓ 许可证信息已设置[/green]")
            return True
        else:
            console.print("\n[red]错误：许可证信息设置失败[/red]")
            return False
    
    def show_generation_options(self):
        """生成选项界面"""
        console.print("\n[bold cyan]第三步：生成选项[/bold cyan]")
        
        questions = [
            inquirer.Text(
                'output_dir',
                message="输出目录",
                default=self.output_dir
            ),
            inquirer.Confirm(
                'regenerate_cert',
                message="是否重新生成证书（如果已存在）",
                default=False
            ),
            inquirer.Confirm(
                'show_license',
                message="是否显示生成的许可证内容",
                default=True
            )
        ]
        
        answers = inquirer.prompt(questions)
        if answers:
            self.output_dir = answers['output_dir']
            self.regenerate_cert = answers['regenerate_cert']
            self.show_license = answers['show_license']
            return True
        return False
    
    def generate_license(self):
        """生成许可证和配置文件"""
        console.print("\n[bold cyan]正在生成许可证和配置文件...[/bold cyan]")
        
        try:
            # 创建输出目录
            os.makedirs(self.output_dir, exist_ok=True)
            cert_dir = os.path.join(self.output_dir, "certificates")
            os.makedirs(cert_dir, exist_ok=True)
            
            cert_file = os.path.join(cert_dir, "ca.crt")
            key_file = os.path.join(cert_dir, "ca.key")
            
            # 生成证书
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("生成RSA证书和私钥...", total=None)
                
                if not os.path.exists(cert_file) or self.regenerate_cert:
                    CertUtil.gen_cert(cert_file, key_file)
                    progress.update(task, description="✓ 证书生成完成")
                else:
                    progress.update(task, description="✓ 使用现有证书")
            
            # 生成power.conf
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("生成power.conf配置文件...", total=None)
                PowerConfigUtil.gen_power_plugin_config(cert_file, self.output_dir)
                progress.update(task, description="✓ power.conf生成完成")
            
            # 生成许可证
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("生成许可证...", total=None)
                
                # 创建自定义许可证
                license_data = {
                    "licenseId": self.license_info["license_id"],
                    "licenseeName": self.license_info["licensee_name"],
                    "licenseeType": "a",
                    "assigneeName": self.license_info["assignee_name"],
                    "assigneeEmail": self.license_info["assignee_email"],
                    "licenseRestriction": self.license_info["license_restriction"],
                    "checkConcurrentUse": False,
                    "products": [],
                    "metadata": "0120230914PSAX000005",
                    "hash": "58003071:-1635216578",
                    "gracePeriodDays": 7,
                    "autoProlongated": True,
                    "isAutoProlongated": True
                }
                
                # 添加产品授权
                for product_code in self.selected_products:
                    product_auth = {
                        "code": product_code,
                        "fallbackDate": self.license_info["expire_date"],
                        "paidUpTo": self.license_info["expire_date"],
                        "extend": True
                    }
                    license_data["products"].append(product_auth)
                
                license_json = json.dumps(license_data, ensure_ascii=False, indent=2)
                progress.update(task, description="✓ 许可证生成完成")
            
            # 生成激活码
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("生成激活码...", total=None)
                active_code = CodeUtil.gen_active_code(cert_file, key_file, license_json)
                progress.update(task, description="✓ 激活码生成完成")
            
            # 保存license到文件
            license_file = os.path.join(self.output_dir, "license.txt")
            with open(license_file, 'w', encoding='utf-8') as f:
                f.write(active_code)
            
            return True, license_json, active_code
            
        except Exception as e:
            console.print(f"\n[red]错误：{e}[/red]")
            return False, None, None
    
    def show_results(self, license_json: str, active_code: str):
        """显示生成结果"""
        console.print("\n" + "="*60)
        console.print("[bold green]✓ 生成完成！[/bold green]")
        console.print("="*60)
        
        # 显示文件信息
        files_table = Table(title="生成的文件", show_header=True, header_style="bold magenta")
        files_table.add_column("文件", style="cyan")
        files_table.add_column("路径", style="green")
        files_table.add_column("说明", style="yellow")
        
        files_table.add_row("证书", os.path.join(self.output_dir, "certificates\\ca.crt"), "RSA证书文件")
        files_table.add_row("私钥", os.path.join(self.output_dir, "certificates\\ca.key"), "RSA私钥文件")
        files_table.add_row("Power配置", os.path.join(self.output_dir, "power.conf"), "Power插件配置")
        files_table.add_row("License", os.path.join(self.output_dir, "license.txt"), "License文件")
        
        console.print(files_table)
        
        # 显示license
        console.print("\n[bold cyan]License：[/bold cyan]")
        console.print(Panel(active_code, style="bold green", box=box.ROUNDED))
        
        # 显示许可证信息
        if self.show_license:
            console.print("\n[bold cyan]许可证信息：[/bold cyan]")
            license_data = json.loads(license_json)
            license_table = Table(show_header=True, header_style="bold magenta")
            license_table.add_column("字段", style="cyan")
            license_table.add_column("值", style="green")
            
            license_table.add_row("许可证ID", license_data["licenseId"])
            license_table.add_row("持有者", license_data["licenseeName"])
            license_table.add_row("被授权人", license_data["assigneeName"])
            license_table.add_row("邮箱", license_data["assigneeEmail"])
            license_table.add_row("过期日期", license_data["products"][0]["paidUpTo"])
            license_table.add_row("产品数量", str(len(license_data["products"])))
            
            console.print(license_table)
        
        # 使用说明
        console.print("\n[bold yellow]使用说明：[/bold yellow]")
        console.print("1. 将 power.conf 文件复制到 jetbra/config-jetbrains 目录")
        console.print("2. 使用生成的license激活JetBrains产品")
        console.print("3. 证书和私钥文件请妥善保管")
        
        # 询问是否自动安装
        if Confirm.ask("\n是否自动安装到JetBrains？", default=True):
            self.auto_install()
    
    def auto_install(self):
        """自动安装到JetBrains"""
        console.print("\n[bold cyan]开始自动安装...[/bold cyan]")
        try:
            # 查找jetbra目录
            jetbra_dir = self.find_jetbra_directory()
            if not jetbra_dir:
                console.print("[red]错误：未找到jetbra目录，请确保已下载jetbra.zip并解压[/red]")
                return
            console.print(f"[green]找到jetbra目录：{jetbra_dir}[/green]")
            # 只复制power.conf文件
            power_conf_src = os.path.join(self.output_dir, "power.conf")
            power_conf_dst = os.path.join(jetbra_dir, "config-jetbrains", "power.conf")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                # 复制power.conf
                task = progress.add_task("复制power.conf文件...", total=None)
                os.makedirs(os.path.dirname(power_conf_dst), exist_ok=True)
                shutil.copy2(power_conf_src, power_conf_dst)
                progress.update(task, description="✓ power.conf复制完成")
            # 用Python实现的卸载和安装
            console.print("\n[bold yellow]正在卸载旧环境变量...[/bold yellow]")
            uninstall_all_users()
            console.print("[bold yellow]正在安装新环境变量...[/bold yellow]")
            install_all_users(jetbra_dir)
            # 复制license到剪贴板
            license_file = os.path.join(self.output_dir, "license.txt")
            if os.path.exists(license_file):
                with open(license_file, 'r', encoding='utf-8') as f:
                    license_content = f.read().strip()
                try:
                    import pyperclip
                    pyperclip.copy(license_content)
                    console.print("✓ License已复制到剪贴板")
                    console.print("[bold green]安装完成！[/bold green]")
                    console.print("现在可以打开JetBrains产品，粘贴license进行激活")
                except ImportError:
                    console.print("[yellow]提示：安装pyperclip可以自动复制license到剪贴板[/yellow]")
                    console.print(f"License内容：{license_content}")
        except Exception as e:
            console.print(f"[red]自动安装失败：{e}[/red]")
            console.print("请手动完成安装步骤")
    
    def find_jetbra_directory(self):
        """查找jetbra目录"""
        # 常见的jetbra目录位置
        possible_paths = [
            "jetbra",  # 当前目录下
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                # 检查是否包含必要的文件
                config_dir = os.path.join(path, "config-jetbrains")
                scripts_dir = os.path.join(path, "scripts")
                
                if os.path.exists(config_dir) and os.path.exists(scripts_dir):
                    return path
        
        return None
    
    def main_menu(self):
        """主菜单，分离生成与安装功能"""
        while True:
            console.print(f"\n[bold magenta]{self.L['main_menu']}[/bold magenta]")
            questions = [
                inquirer.List(
                    'action',
                    message=self.L['main_menu'],
                    choices=[
                        (self.L['generate'], "generate"),
                        (self.L['install'], "install"),
                        (self.L['language'], "language"),
                        (self.L['exit'], "exit")
                    ]
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers or answers['action'] == 'exit':
                console.print(f"\n[bold yellow]{self.L['exit_msg']}[/bold yellow]")
                break
            elif answers['action'] == 'generate':
                self.handle_generate()
            elif answers['action'] == 'install':
                self.handle_install()
            elif answers['action'] == 'language':
                self.handle_language()

    def handle_generate(self):
        # 第一步：产品选择
        if not self.show_product_selection():
            return
        # 第二步：许可证自定义
        if not self.show_license_customization():
            return
        # 第三步：生成选项
        if not self.show_generation_options():
            return
        # 第四步：生成许可证
        success, license_json, active_code = self.generate_license()
        if success:
            self.show_results(license_json, active_code)
        else:
            console.print("\n[red]生成失败，请检查错误信息[/red]")

    def handle_install(self):
        # 检查必要文件是否存在
        power_conf = os.path.join(self.output_dir, "power.conf")
        license_txt = os.path.join(self.output_dir, "license.txt")
        if not os.path.exists(power_conf) or not os.path.exists(license_txt):
            console.print("[red]未找到 power.conf 或 license.txt，请先生成！[/red]")
            return
        self.auto_install()

    def handle_language(self):
        questions = [
            inquirer.List(
                'lang',
                message=self.L['select_language'],
                choices=[(self.L['lang_en'], 'en'), (self.L['lang_zh'], 'zh')]
            )
        ]
        answers = inquirer.prompt(questions)
        if answers and answers['lang'] in LANGUAGES:
            self.set_language(answers['lang'])
            console.print(f"[green]Language switched to {self.L['lang_en'] if self.language == 'en' else self.L['lang_zh']}[/green]")

    def run(self):
        """运行CLI工具"""
        self.show_banner()
        try:
            self.main_menu()
        except KeyboardInterrupt:
            console.print("\n[yellow]用户取消操作[/yellow]")
        except Exception as e:
            console.print(f"\n[red]程序错误：{e}[/red]")


def main():
    """主函数"""
    cli = JetBrainsCLI()
    cli.run()


if __name__ == "__main__":
    main() 