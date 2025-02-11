#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import ctypes
import requests
from datetime import datetime
import subprocess
import msvcrt  # Windows系统下的键盘输入处理
from colorama import init, Fore, Style
import time
import threading

# 初始化colorama
init(autoreset=True)

# 常量定义
if sys.platform == 'win32':
    HOSTS_PATH = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', 'drivers', 'etc', 'hosts')
elif sys.platform == 'darwin':  # macOS
    HOSTS_PATH = '/private/etc/hosts'
else:  # Linux, BSD 等类Unix系统
    HOSTS_PATH = '/etc/hosts'

GITHUB520_START = "# GitHub520 Host Start"
GITHUB520_END = "# GitHub520 Host End"

# ASCII 艺术字
ASCII_ART = f'''

   ██████╗ ██╗████████╗██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗  ██████╗ 
  ██╔════╝ ██║╚══██╔══╝██║  ██║██║   ██║██╔══██╗██╔════╝╚════██╗██╔═══██╗
  ██║  ███╗██║   ██║   ███████║██║   ██║██████╔╝███████╗ █████╔╝██║   ██║
  ██║   ██║██║   ██║   ██╔══██║██║   ██║██╔══██╗╚════██║██╔═══╝ ██║   ██║
  ╚██████╔╝██║   ██║   ██║  ██║╚██████╔╝██████╔╝███████║███████╗╚██████╔╝
   ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ 
'''

# 项目信息
PROJECT_INFO = f'''{Fore.GREEN}
项目来源: https://github.com/521xueweihan/GitHub520
项目简介: 😘 让你"爱"上 GitHub，解决访问时图裂、加载慢的问题。
鸣谢: 感谢「削微寒」开源分享，帮助开发者便捷访问 GitHub！
{Style.RESET_ALL}'''

# Hosts 源
HOSTS_URLS = [
    "https://raw.hellogithub.com/hosts"
]

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_hosts_content(urls):
    """从多个URL获取hosts内容"""
    session = requests.Session()  # 使用会话提升连接效率
    for url in urls:
        try:
            response = session.get(url, timeout=5)  # 减少超时时间
            if response.status_code == 200:
                if url.endswith('.json'):
                    return '\n'.join(f"{ip} {domain}" for ip, domain in response.json().items())
                return response.text
        except Exception as e:
            print(f"从 {url} 获取数据失败: {str(e)}")
    return None

def manage_backups():
    """管理备份文件，只保留最新的3个备份"""
    try:
        backup_dir = os.path.dirname(HOSTS_PATH)
        # 获取所有备份文件
        backup_files = [f for f in os.listdir(backup_dir) 
                       if f.startswith('hosts.') and f.endswith('.bak')]
        
        # 如果备份文件超过3个
        if len(backup_files) > 3:
            # 按修改时间排序
            backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
            # 删除最旧的文件，直到只剩3个
            for f in backup_files[:-3]:
                try:
                    os.remove(os.path.join(backup_dir, f))
                except:
                    continue
    except:
        pass  # 如果管理备份失败，不影响主要功能

def update_hosts():
    """更新hosts文件"""
    if not is_admin():
        print("🔒 请以管理员权限运行此脚本！")
        return

    # 备份原hosts文件
    try:
        with open(HOSTS_PATH, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 使用更简洁的备份文件名
        backup_name = f"hosts.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        backup_path = os.path.join(os.path.dirname(HOSTS_PATH), backup_name)
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"{Fore.CYAN}💾 已备份原hosts文件：")
        print(f"   📂 备份路径：{backup_path}{Style.RESET_ALL}")
        
        # 管理备份文件
        manage_backups()
    except Exception as e:
        print(f"❌ 备份hosts文件失败: {str(e)}")
        return

    # 获取新的hosts内容
    new_hosts = get_hosts_content(HOSTS_URLS)
    if not new_hosts:
        print("❌ 获取新hosts内容失败！")
        return

    try:
        # 清理所有GitHub520相关内容
        lines = original_content.splitlines()
        cleaned_lines = []
        is_github520_section = False
        
        for line in lines:
            # 跳过GitHub520的开始标记
            if GITHUB520_START in line:
                is_github520_section = True
                continue
            # 跳过GitHub520的结束标记
            if GITHUB520_END in line:
                is_github520_section = False
                continue
            # 只保留非GitHub520部分的内容
            if not is_github520_section:
                cleaned_lines.append(line)
        
        # 清理末尾的空行
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        # 写入新的hosts文件
        with open(HOSTS_PATH, 'w', encoding='utf-8') as f:
            if cleaned_lines:
                f.write('\n'.join(cleaned_lines) + '\n\n')
            f.write(f"{GITHUB520_START}\n{new_hosts}\n{GITHUB520_END}\n")

        # 使用subprocess执行命令并抑制输出
        subprocess.run(['ipconfig', '/flushdns'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{Fore.GREEN}✨ hosts文件更新成功！\n✨ DNS缓存已刷新。{Style.RESET_ALL}")
    except Exception as e:
        print(f"❌ 更新hosts文件失败: {str(e)}")
        try:
            with open(HOSTS_PATH, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print("↩️ 已恢复原hosts文件")
        except:
            print("❌ 恢复原hosts文件失败！")

def open_editor(file_path):
    """使用系统默认编辑器打开文件"""
    try:
        if sys.platform == 'win32':
            os.system(f'notepad "{file_path}"')
        else:
            editor = os.getenv('EDITOR', 'vim')
            subprocess.call([editor, file_path])
        return True
    except Exception as e:
        print(f"❌ 打开编辑器失败: {str(e)}")
        return False

def edit_hosts():
    """编辑hosts文件"""
    if not is_admin():
        print("🔒 请以管理员权限运行此脚本！")
        return

    try:
        print(f"\n{Fore.YELLOW}📝 正在打开编辑器...{Style.RESET_ALL}")
        if open_editor(HOSTS_PATH):
            print(f"{Fore.GREEN}✨ 编辑完成！{Style.RESET_ALL}")
            # 使用subprocess执行命令并抑制输出
            subprocess.run(['ipconfig', '/flushdns'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Fore.GREEN}✨ DNS缓存已刷新{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ 编辑hosts文件失败: {str(e)}{Style.RESET_ALL}")

def get_valid_input(prompt, valid_choices):
    """获取有效的用户输入，只允许输入选项数字且需要回车确认"""
    while True:
        print(prompt, end='', flush=True)
        input_str = ''
        while True:
            try:
                char = msvcrt.getch().decode()
                # 如果是回车键
                if char == '\r':
                    if input_str in valid_choices:
                        print()  # 换行
                        return input_str
                    else:
                        print()  # 换行
                        break  # 重新开始输入
                # 如果是退格键
                elif char == '\b':
                    if input_str:
                        input_str = ''
                        print('\b \b', end='', flush=True)
                # 如果是有效的选项数字且还未输入
                elif not input_str and char in valid_choices:
                    input_str = char
                    print(char, end='', flush=True)
                # 忽略其他所有输入
                else:
                    continue
            except (EOFError, KeyboardInterrupt):
                print("\n👋 感谢使用！再见！")
                sys.exit(0)
            except:
                continue  # 忽略解码错误等其他异常

def refresh_dns():
    """刷新DNS缓存"""
    try:
        # 使用subprocess执行命令并抑制输出
        subprocess.run(['ipconfig', '/flushdns'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{Fore.GREEN}✨ DNS缓存刷新成功！{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ DNS缓存刷新失败: {str(e)}{Style.RESET_ALL}")
        return False

def refresh_screen():
    """刷新屏幕显示"""
    input("\n按回车键继续...")  # 等待用户确认
    os.system('cls')  # 清屏
    print(ASCII_ART)  # 重新显示界面
    print(PROJECT_INFO)

def open_hosts_location():
    """打开hosts文件所在目录"""
    try:
        hosts_dir = os.path.dirname(HOSTS_PATH)
        if sys.platform == 'win32':
            os.system(f'explorer "{hosts_dir}"')
        else:
            if sys.platform == 'darwin':  # macOS
                os.system(f'open "{hosts_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{hosts_dir}"')
        print(f"{Fore.GREEN}✨ 已打开hosts文件所在目录：{Style.RESET_ALL}")
        print(f"   📂 {hosts_dir}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ 打开目录失败: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """主函数"""
    # 设置命令窗口标题（不显示管理员或用户名）
    if sys.platform == 'win32':
        ctypes.windll.kernel32.SetConsoleTitleW("GitHub520 加速工具 v1.0.0")
    
    print(ASCII_ART)
    print(PROJECT_INFO)
    
    valid_choices = {'1', '2', '3', '4', '5', '6'}
    
    while True:
        print(f"\n{Fore.YELLOW}请选择操作：{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. 更新 GitHub 加速配置{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. 刷新 DNS 缓存{Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. 查看 hosts 内容{Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. 手动编辑 hosts{Style.RESET_ALL}")
        print(f"{Fore.WHITE}5. 打开 hosts 文件目录{Style.RESET_ALL}")
        print(f"{Fore.WHITE}6. 退出程序{Style.RESET_ALL}")
        
        choice = get_valid_input(f"\n{Fore.CYAN}请输入选项数字 (1-6): {Style.RESET_ALL}", valid_choices)
        
        if choice == '1':
            print(f"\n{Fore.YELLOW}🔄 正在更新hosts...{Style.RESET_ALL}")
            try:
                update_hosts()
                print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")  # 成功时显示绿色分割线
                input("\n按回车键继续...")  # 等待用户确认
                os.system('cls')  # 清屏
                print(ASCII_ART)  # 重新显示界面
                print(PROJECT_INFO)
            except Exception as e:
                print(f"\n{Fore.RED}{'='*50}{Style.RESET_ALL}")  # 失败时显示红色分割线
                input("\n按回车键继续...")  # 等待用户确认
                os.system('cls')  # 清屏
                print(ASCII_ART)  # 重新显示界面
                print(PROJECT_INFO)
        elif choice == '2':
            try:
                print(f"\n{Fore.YELLOW}🔄 正在刷新DNS缓存...{Style.RESET_ALL}")
                refresh_dns()
                print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")  # 成功时显示绿色分割线
                refresh_screen()
            except Exception as e:
                print(f"\n{Fore.RED}{'='*50}{Style.RESET_ALL}")  # 失败时显示红色分割线
                refresh_screen()
        elif choice == '3':
            try:
                with open(HOSTS_PATH, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                print(f"\n{Fore.CYAN}📄 当前hosts文件内容：\n{Style.RESET_ALL}")
                print(content if content else f"{Fore.YELLOW}📝 hosts内容为空！{Style.RESET_ALL}")
                print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")  # 成功时显示绿色分割线
                refresh_screen()
            except Exception as e:
                print(f"{Fore.RED}❌ 读取hosts文件失败: {str(e)}")
                print(f"\n{Fore.RED}{'='*50}{Style.RESET_ALL}")  # 失败时显示红色分割线
                refresh_screen()
        elif choice == '4':
            try:
                edit_hosts()
                print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")  # 成功时显示绿色分割线
                refresh_screen()
            except Exception as e:
                print(f"\n{Fore.RED}{'='*50}{Style.RESET_ALL}")  # 失败时显示红色分割线
                refresh_screen()
        elif choice == '5':
            try:
                open_hosts_location()
                print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")  # 成功时显示绿色分割线
                refresh_screen()
            except Exception as e:
                print(f"\n{Fore.RED}{'='*50}{Style.RESET_ALL}")  # 失败时显示红色分割线
                refresh_screen()
        elif choice == '6':
            print(f"\n{Fore.GREEN}👋 感谢使用！再见！{Style.RESET_ALL}")
            print(f"\n{Fore.GREEN}{'='*50}{Style.RESET_ALL}")  # 退出时显示绿色分割线
            break

if __name__ == "__main__":
    try:
        if not is_admin():
            if sys.platform == 'win32':
                # 使用管理员权限重新启动程序
                script = os.path.abspath(sys.argv[0])
                params = ' '.join([script] + sys.argv[1:])
                ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                if ret > 32:  # 如果成功启动
                    sys.exit(0)
                else:
                    print("🔒 无法获取管理员权限，请手动以管理员身份运行！")
                    input("\n按回车键退出...")
                    sys.exit(1)
            else:
                print("🔒 请以管理员权限运行此脚本！")
                sys.exit(1)
        else:
            main()
    except Exception as e:
        print(f"❌ 程序运行出错: {str(e)}")
        input("\n按回车键退出...") 