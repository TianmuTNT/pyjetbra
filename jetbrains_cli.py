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

# 多语言文件路径
LANGUAGE_FILES = {
    'en': 'language/en.json',
    'zh': 'language/zh.json'
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

def load_language(lang):
    path = LANGUAGE_FILES.get(lang, LANGUAGE_FILES['en'])
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Language file not found: {path}")

class JetBrainsCLI:
    """JetBrains许可证生成CLI工具"""
    
    API_URL = "https://account.jetbrains.com/services/rest/coupon/v1/redeem/items/personal"
    
    def __init__(self):
        self.selected_products = []
        self.license_info = {}
        self.output_dir = "out"
        self.config = load_config()
        self.language = self.config.get('language', 'en')
        self.L = load_language(self.language)
    
    def set_language(self, lang):
        self.language = lang
        self.L = load_language(self.language)
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
        console.print(f"\n[bold cyan]{self.L['product_step']}[/bold cyan]")
        console.print(f"{self.L['product_api']}\n")
        all_products = self.fetch_all_products()
        # 构建分组展示
        table = Table(title=self.L['product_table'], show_header=True, header_style="bold magenta")
        table.add_column(self.L['product_code'], style="cyan", width=10)
        table.add_column(self.L['product_group'], style="yellow", width=10)
        table.add_column(self.L['product_name'], style="green", width=40)
        for item in all_products:
            table.add_row(item["code"], item["group"], item["name"])
        console.print(table)
        # 构建多选菜单
        choices = [(f"[{item['group']}] {item['name']}", item["code"]) for item in all_products]
        questions = [
            inquirer.Checkbox(
                'products',
                message=self.L['product_select'],
                choices=[(self.L['product_all'], "ALL")] + choices
            )
        ]
        answers = inquirer.prompt(questions)
        if answers and answers['products']:
            if "ALL" in answers['products']:
                self.selected_products = [item["code"] for item in all_products]
            else:
                self.selected_products = answers['products']
            console.print(f"\n[green]✓ {self.L['product_selected'].format(count=len(self.selected_products))}[/green]")
        else:
            console.print(f"\n[red]{self.L['product_error']}[/red]")
            return False
        return True
    
    def show_license_customization(self):
        console.print(f"\n[bold cyan]{self.L['license_step']}[/bold cyan]")
        console.print(f"{self.L['license_tip']}\n")
        # 默认值
        default_licensee_name = "Your Name"
        default_assignee_name = "Your Company"
        default_assignee_email = "your.email@example.com"
        default_expire_date = "2099-12-31"
        default_license_restriction = "Generated by JetBrains License Generator"
        questions = [
            inquirer.Text(
                'licensee_name',
                message=self.L['licensee_name'],
                default=default_licensee_name
            ),
            inquirer.Text(
                'assignee_name',
                message=self.L['assignee_name'],
                default=default_assignee_name
            ),
            inquirer.Text(
                'assignee_email',
                message=self.L['assignee_email'],
                default=default_assignee_email
            ),
            inquirer.Text(
                'expire_date',
                message=self.L['expire_date'],
                default=default_expire_date
            ),
            inquirer.Text(
                'license_restriction',
                message=self.L['license_restriction'],
                default=default_license_restriction
            ),
            inquirer.Text(
                'license_id',
                message=self.L['license_id'],
                default="CUSTOM_LICENSE"
            )
        ]
        answers = inquirer.prompt(questions)
        if answers:
            self.license_info = answers
            console.print(f"\n[green]✓ {self.L['license_set']}[/green]")
            return True
        else:
            console.print(f"\n[red]{self.L['license_error']}[/red]")
            return False
    
    def show_generation_options(self):
        console.print(f"\n[bold cyan]{self.L['gen_step']}[/bold cyan]")
        questions = [
            inquirer.Text(
                'output_dir',
                message=self.L['output_dir'],
                default=self.output_dir
            ),
            inquirer.Confirm(
                'regenerate_cert',
                message=self.L['regenerate_cert'],
                default=False
            ),
            inquirer.Confirm(
                'show_license',
                message=self.L['show_license'],
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
        console.print(f"[bold green]✓ {self.L['gen_success']}[/bold green]")
        console.print("="*60)
        files_table = Table(title=self.L['file_table'], show_header=True, header_style="bold magenta")
        files_table.add_column(self.L['file'], style="cyan")
        files_table.add_column(self.L['path'], style="green")
        files_table.add_column(self.L['desc'], style="yellow")
        files_table.add_row(self.L['cert_file'], os.path.join(self.output_dir, "certificates\\ca.crt"), self.L['cert_desc'])
        files_table.add_row(self.L['key_file'], os.path.join(self.output_dir, "certificates\\ca.key"), self.L['key_desc'])
        files_table.add_row(self.L['power_file'], os.path.join(self.output_dir, "power.conf"), self.L['power_desc'])
        files_table.add_row(self.L['license_file'], os.path.join(self.output_dir, "license.txt"), self.L['license_desc'])
        console.print(files_table)
        console.print(f"\n[bold cyan]{self.L['license_panel']}[/bold cyan]")
        console.print(Panel(active_code, style="bold green", box=box.ROUNDED))
        if self.show_license:
            console.print(f"\n[bold cyan]{self.L['license_info']}[/bold cyan]")
            license_data = json.loads(license_json)
            license_table = Table(show_header=True, header_style="bold magenta")
            license_table.add_column(self.L['license_id2'], style="cyan")
            license_table.add_column(self.L['licensee'], style="green")
            license_table.add_column(self.L['assignee'], style="green")
            license_table.add_column(self.L['email'], style="green")
            license_table.add_column(self.L['expiry'], style="green")
            license_table.add_column(self.L['product_count'], style="green")
            license_table.add_row(
                license_data["licenseId"],
                license_data["licenseeName"],
                license_data["assigneeName"],
                license_data["assigneeEmail"],
                license_data["products"][0]["paidUpTo"],
                str(len(license_data["products"]))
            )
            console.print(license_table)
        console.print(f"\n[bold yellow]{self.L['usage']}[/bold yellow]")
        console.print(self.L['usage1'])
        console.print(self.L['usage2'])
        console.print(self.L['usage3'])
        if Confirm.ask(f"\n{self.L['install']}?", default=True):
            self.auto_install()
    
    def auto_install(self):
        """自动安装到JetBrains"""
        console.print(f"\n[bold cyan]{self.L['auto_install']}[/bold cyan]")
        try:
            jetbra_dir = self.find_jetbra_directory()
            if not jetbra_dir:
                console.print(f"[red]{self.L['find_jetbra_fail']}[/red]")
                return
            console.print(f"[green]{self.L['find_jetbra']} {jetbra_dir}[/green]")
            power_conf_src = os.path.join(self.output_dir, "power.conf")
            power_conf_dst = os.path.join(jetbra_dir, "config-jetbrains", "power.conf")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(self.L['copy_power'], total=None)
                os.makedirs(os.path.dirname(power_conf_dst), exist_ok=True)
                shutil.copy2(power_conf_src, power_conf_dst)
                progress.update(task, description=f"✓ {self.L['copy_done']}")
            console.print(f"\n[bold yellow]{self.L['uninstall_env']}[/bold yellow]")
            uninstall_all_users()
            console.print(f"[bold yellow]{self.L['install_env']}[/bold yellow]")
            install_all_users(jetbra_dir)
            license_file = os.path.join(self.output_dir, "license.txt")
            if os.path.exists(license_file):
                with open(license_file, 'r', encoding='utf-8') as f:
                    license_content = f.read().strip()
                try:
                    import pyperclip
                    pyperclip.copy(license_content)
                    console.print(f"✓ {self.L['copy_clipboard']}")
                    console.print(f"[bold green]{self.L['install_done']}[/bold green]")
                    console.print(self.L['open_jetbrains'])
                except ImportError:
                    console.print(f"[yellow]{self.L['pyperclip_tip']}[/yellow]")
                    console.print(f"{self.L['license_content']} {license_content}")
        except Exception as e:
            console.print(f"[red]{self.L['auto_install_fail']} {e}[/red]")
            console.print(self.L['manual_install'])
    
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
    
    def show_about(self):
        """显示关于信息"""
        console.print(Panel(f"[bold]{self.L['about_title']}[/bold]\n\n"
                           f"{self.L['about_repo']}\n"
                           f"{self.L['about_license']}\n\n"
                           f"{self.L['about_disclaimer']}",
                           title=self.L['about'], style="bold blue", box=box.ROUNDED))
    
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
                        (self.L['about'], "about"),
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
            elif answers['action'] == 'about':
                self.show_about()

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
        power_conf = os.path.join(self.output_dir, "power.conf")
        license_txt = os.path.join(self.output_dir, "license.txt")
        if not os.path.exists(power_conf) or not os.path.exists(license_txt):
            console.print(f"[red]{self.L['not_found']}[/red]")
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
        if answers and answers['lang'] in LANGUAGE_FILES:
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