import os
import sys
import re
import platform
from pathlib import Path

if os.name == 'nt':
    import winreg
    import ctypes

JB_PRODUCTS = [
    "idea", "clion", "phpstorm", "goland", "pycharm", "webstorm", "webide", "rider", "datagrip", "rubymine", "dataspell", "aqua", "rustrover", "gateway", "jetbrains_client", "jetbrainsclient", "studio", "devecostudio"
]

# 管理员权限提升

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join([sys.argv[0]] + sys.argv[1:]), None, 1)
        sys.exit(0)

# 刷新环境变量

def refresh_env():
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    SMTO_ABORTIFHUNG = 0x0002
    result = ctypes.c_long()
    ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))

# 获取环境变量

def get_env(var, system=False):
    try:
        if system:
            root = winreg.HKEY_LOCAL_MACHINE
            path = r'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
        else:
            root = winreg.HKEY_CURRENT_USER
            path = r'Environment'
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
            return winreg.QueryValueEx(key, var)[0]
    except FileNotFoundError:
        return None
    except Exception:
        return None

# 删除环境变量

def remove_env(var, system=False):
    if get_env(var, system) is not None:
        try:
            if system:
                root = winreg.HKEY_LOCAL_MACHINE
                path = r'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
            else:
                root = winreg.HKEY_CURRENT_USER
                path = r'Environment'
            with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, var)
        except FileNotFoundError:
            pass
        except Exception:
            pass

# 设置系统环境变量

def set_system_env(var, value):
    try:
        root = winreg.HKEY_LOCAL_MACHINE
        path = r'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
        with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, var, 0, winreg.REG_EXPAND_SZ, value)
    except Exception as e:
        print(f"[警告] 设置系统环境变量失败: {var}={value} ({e})")

# VBS风格弹窗

def msgbox(msg):
    ctypes.windll.user32.MessageBoxW(0, msg, "JetBrains Environment Tool", 0)

# 卸载所有用户和系统环境变量

def uninstall_all_users():
    os_type = get_os()
    if os_type == "windows":
        elevate()
        msgbox("It may take a few seconds to execute this script.\n\nClick 'OK' button and wait for the prompt of 'Done.' to pop up!")
        for prd in JB_PRODUCTS:
            var = f"{prd.upper()}_VM_OPTIONS"
            remove_env(var, system=False)
            remove_env(var, system=True)
        refresh_env()
        msgbox("Done.")
        print("卸载完成。")
        return
    # Linux/macOS
    print("正在卸载 JetBrains 环境变量 (Linux/macOS)...")
    home = str(Path.home())
    kde_env_dir = os.path.join(home, ".config/plasma-workspace/env")
    my_vmoptions_shell_name = "jetbrains.vmoptions.sh"
    my_vmoptions_shell_file = os.path.join(home, f".{my_vmoptions_shell_name}")
    plist_path = os.path.join(home, "Library/LaunchAgents/jetbrains.vmoptions.plist")
    # 删除自定义 shell 文件
    if os.path.exists(my_vmoptions_shell_file):
        os.remove(my_vmoptions_shell_file)
    # macOS: unset launchctl
    if os_type == "macos":
        for prd in JB_PRODUCTS:
            env_name = f"{prd.upper()}_VM_OPTIONS"
            os.system(f"launchctl unsetenv {env_name}")
        if os.path.exists(plist_path):
            os.remove(plist_path)
    # 删除 profile 里的自动加载行
    exec_line = r'___MY_VMOPTIONS_SHELL_FILE="\${HOME}/\.jetbrains\.vmoptions\.sh"; if '  # 用于sed删除
    for profile in get_shell_profiles():
        remove_line_from_file(profile, exec_line)
    # KDE
    if os_type != "macos":
        if os.path.exists(os.path.join(kde_env_dir, my_vmoptions_shell_name)):
            os.remove(os.path.join(kde_env_dir, my_vmoptions_shell_name))
    print("done. you'd better log off first!" if os_type != "macos" else "done.")

# 安装所有用户环境变量

def install_all_users(jetbra_dir):
    os_type = get_os()
    if os_type == "windows":
        elevate()
        sBasePath = Path(jetbra_dir).resolve()
        jar_file = sBasePath / "ja-netfilter.jar"
        vmoptions_dir = sBasePath / "vmoptions"
        if not jar_file.exists():
            msgbox("ja-netfilter.jar not found")
            return False
        msgbox("It may take a few seconds to execute this script.\n\nClick 'OK' button and wait for the prompt of 'Done.' to pop up!")
        for prd in JB_PRODUCTS:
            var = f"{prd.upper()}_VM_OPTIONS"
            remove_env(var, system=False)
        pattern = re.compile(r"^-javaagent:.*[\\/\\\\]ja\-netfilter\.jar.*", re.I)
        for prd in JB_PRODUCTS:
            var = f"{prd.upper()}_VM_OPTIONS"
            vm_file = vmoptions_dir / f"{prd}.vmoptions"
            if not vm_file.exists():
                continue
            with open(vm_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            sNewContent = ''
            for line in lines:
                if not pattern.match(line.strip()):
                    sNewContent += line.rstrip('\r\n') + '\n'
            sNewContent += f"-javaagent:{jar_file}=jetbrains"
            with open(vm_file, 'w', encoding='utf-8') as f:
                f.write(sNewContent)
            set_system_env(var, str(vm_file))
        refresh_env()
        msgbox("Done.")
        print("安装完成。")
        return True
    # Linux/macOS
    print("正在安装 JetBrains 环境变量 (Linux/macOS)...")
    home = str(Path.home())
    base_path = os.path.abspath(os.path.join(jetbra_dir))
    jar_file_path = os.path.join(base_path, "ja-netfilter.jar")
    vmoptions_dir = os.path.join(base_path, "vmoptions")
    kde_env_dir = os.path.join(home, ".config/plasma-workspace/env")
    launch_agents_dir = os.path.join(home, "Library/LaunchAgents")
    plist_path = os.path.join(launch_agents_dir, "jetbrains.vmoptions.plist")
    my_vmoptions_shell_name = "jetbrains.vmoptions.sh"
    my_vmoptions_shell_file = os.path.join(home, f".{my_vmoptions_shell_name}")
    exec_line = '___MY_VMOPTIONS_SHELL_FILE="${HOME}/.jetbrains.vmoptions.sh"; if [ -f "${___MY_VMOPTIONS_SHELL_FILE}" ]; then . "${___MY_VMOPTIONS_SHELL_FILE}"; fi'
    # 生成 shell 文件
    with open(my_vmoptions_shell_file, 'w', encoding='utf-8') as f:
        f.write('#!/bin/sh\n')
    # 处理每个产品
    for prd in JB_PRODUCTS:
        vm_file_path = os.path.join(vmoptions_dir, f"{prd}.vmoptions")
        if not os.path.exists(vm_file_path):
            continue
        # 移除旧的-javaagent行
        with open(vm_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(vm_file_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if not re.match(r"^-javaagent:.*[\\/\\\\]ja\-netfilter\.jar.*", line.strip(), re.I):
                    f.write(line.rstrip('\r\n') + '\n')
            f.write(f"-javaagent:{jar_file_path}=jetbrains\n")
        env_name = f"{prd.upper()}_VM_OPTIONS"
        with open(my_vmoptions_shell_file, 'a', encoding='utf-8') as f:
            f.write(f'export {env_name}="{vm_file_path}"\n')
        if os_type == "macos":
            # launchctl setenv
            os.system(f'launchctl setenv {env_name} "{vm_file_path}"')
            # 写入plist
            if not os.path.exists(launch_agents_dir):
                os.makedirs(launch_agents_dir)
            with open(plist_path, 'w', encoding='utf-8') as pf:
                pf.write('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>Label</key><string>jetbrains.vmoptions</string><key>ProgramArguments</key><array><string>sh</string><string>-c</string><string>')
                for prd2 in JB_PRODUCTS:
                    env_name2 = f"{prd2.upper()}_VM_OPTIONS"
                    pf.write(f'launchctl setenv \"{env_name2}\" \"{os.path.join(vmoptions_dir, f"{prd2}.vmoptions")}\"; ')
                pf.write('</string></array><key>RunAtLoad</key><true/></dict></plist>')
    # 删除 profile 里的自动加载行
    for profile in get_shell_profiles():
        remove_line_from_file(profile, r'___MY_VMOPTIONS_SHELL_FILE="\${HOME}/\.jetbrains\.vmoptions\.sh"; if ')
    # 添加自动加载行
    for profile in get_shell_profiles():
        with open(profile, 'a', encoding='utf-8') as f:
            f.write(f'\n{exec_line}\n')
    # KDE
    if os_type != "macos":
        if not os.path.exists(kde_env_dir):
            os.makedirs(kde_env_dir)
        kde_env_file = os.path.join(kde_env_dir, my_vmoptions_shell_name)
        if os.path.exists(kde_env_file):
            os.remove(kde_env_file)
        os.symlink(my_vmoptions_shell_file, kde_env_file)
    print("done. you'd better log off first!" if os_type != "macos" else "done. the 'kill Dock' command can fix the crash issue.")
    return True

# ---------------- Linux/macOS 逻辑 ----------------

def get_os():
    sysname = platform.system()
    if sysname == "Windows":
        return "windows"
    elif sysname == "Darwin":
        return "macos"
    else:
        return "linux"

def get_shell_profiles():
    home = str(Path.home())
    profiles = [os.path.join(home, ".profile"), os.path.join(home, ".bashrc"), os.path.join(home, ".zshrc")]
    if get_os() == "macos":
        profiles.append(os.path.join(home, ".bash_profile"))
    return profiles

def remove_line_from_file(filepath, pattern):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            if not re.search(pattern, line):
                f.write(line) 