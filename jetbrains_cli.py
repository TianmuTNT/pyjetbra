#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
import subprocess
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich import box

from cert_util import CertUtil
from code_util import CodeUtil
from power_config_util import PowerConfigUtil
from jetbrains_env import uninstall_all_users, install_all_users

console = Console()


class JetBrainsCLI:
    """JetBrains许可证生成CLI工具"""
    
    # JetBrains产品列表（从官方API获取）
    PRODUCTS = {
        "CL": {"name": "CLion", "description": "C/C++ IDE"},
        "CDGC": {"name": "Cadence Credit", "description": "Cadence Credit"},
        "DB": {"name": "DataGrip", "description": "Database IDE"},
        "DS": {"name": "DataSpell", "description": "Data Science IDE"},
        "DLGC": {"name": "Datalore Credit", "description": "Datalore Credit"},
        "DLP": {"name": "Datalore Professional", "description": "Datalore Professional"},
        "GO": {"name": "GoLand", "description": "Go IDE"},
        "II": {"name": "IntelliJ IDEA Ultimate", "description": "Java IDE"},
        "AIP": {"name": "JetBrains AI Pro", "description": "AI Pro"},
        "AIPU": {"name": "JetBrains AI Ultimate", "description": "AI Ultimate"},
        "ACD": {"name": "JetBrains Academy", "description": "Academy"},
        "PS": {"name": "PhpStorm", "description": "PHP IDE"},
        "PC": {"name": "PyCharm", "description": "Python IDE"},
        "RS0": {"name": "ReSharper", "description": "ReSharper"},
        "RC": {"name": "ReSharper C++", "description": "ReSharper C++"},
        "RD": {"name": "Rider", "description": ".NET IDE"},
        "RM": {"name": "RubyMine", "description": "Ruby IDE"},
        "RR": {"name": "RustRover", "description": "Rust IDE"},
        "WS": {"name": "WebStorm", "description": "JavaScript IDE"}
    }
    
    def __init__(self):
        self.selected_products = []
        self.license_info = {}
        self.output_dir = "out"
    
    def show_banner(self):
        """显示欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    JetBrains License Generator               ║
║                       许可证生成工具                         ║
╚══════════════════════════════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold blue", box=box.DOUBLE))
    
    def show_product_selection(self):
        """产品选择界面"""
        console.print("\n[bold cyan]第一步：选择要激活的产品[/bold cyan]")
        console.print("您可以选择多个产品，也可以一键选择全部产品。\n")
        
        # 创建产品表格
        table = Table(title="可用的JetBrains产品", show_header=True, header_style="bold magenta")
        table.add_column("代码", style="cyan", width=8)
        table.add_column("产品名称", style="green", width=20)
        table.add_column("描述", style="yellow", width=30)
        
        for code, info in self.PRODUCTS.items():
            table.add_row(code, info["name"], info["description"])
        
        console.print(table)
        
        # 产品选择选项
        questions = [
            inquirer.Checkbox(
                'products',
                message="请选择要激活的产品（空格选择，回车确认）",
                choices=[
                    ("全部产品", "ALL"),
                    ("CLion", "CL"),
                    ("Cadence Credit", "CDGC"),
                    ("DataGrip", "DB"),
                    ("DataSpell", "DS"),
                    ("Datalore Credit", "DLGC"),
                    ("Datalore Professional", "DLP"),
                    ("GoLand", "GO"),
                    ("IntelliJ IDEA Ultimate", "II"),
                    ("JetBrains AI Pro", "AIP"),
                    ("JetBrains AI Ultimate", "AIPU"),
                    ("JetBrains Academy", "ACD"),
                    ("PhpStorm", "PS"),
                    ("PyCharm", "PC"),
                    ("ReSharper", "RS0"),
                    ("ReSharper C++", "RC"),
                    ("Rider", "RD"),
                    ("RubyMine", "RM"),
                    ("RustRover", "RR"),
                    ("WebStorm", "WS")
                ]
            )
        ]
        
        answers = inquirer.prompt(questions)
        if answers and answers['products']:
            self.selected_products = answers['products']
            if "ALL" in self.selected_products:
                self.selected_products = list(self.PRODUCTS.keys())
            
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
    
    def run(self):
        """运行CLI工具"""
        self.show_banner()
        
        try:
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