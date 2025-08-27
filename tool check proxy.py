import sys
import subprocess
import pkg_resources

# Import Rich first
from rich.console import Console

def check_and_install_dependencies():
    required_packages = {
        'httpx': 'httpx',
        'colorama': 'colorama',
        'aiohttp': 'aiohttp',
        'rich': 'rich',
        'psutil': 'psutil'
    }
    
    console = Console()
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = [pkg for pkg, import_name in required_packages.items() 
                       if pkg not in installed_packages]
    
    if missing_packages:
        console.print("[yellow]Installing missing dependencies...[/yellow]")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                console.print(f"[green]Successfully installed {package}[/green]")
            except:
                console.print(f"[red]Failed to install {package}[/red]")
                sys.exit(1)

# Check and install dependencies first
console = Console()
console.print("[cyan]Checking dependencies...[/cyan]")
check_and_install_dependencies()

# Now import all required packages
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
import colorama
import hashlib
import httpx
import json
import math
import os
import platform
import psutil
import random
import re
import threading
import time
from colorama import Fore, Style
from datetime import datetime, timedelta
from rich.align import Align
from rich.box import ROUNDED
from rich.panel import Panel
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TaskProgressColumn, 
    TimeElapsedColumn
)
from rich.table import Table
from rich.text import Text
from tkinter import Tk, filedialog

colorama.init(autoreset=True)

def create_rainbow_text_animated(text, time_offset=0):
    rainbow_text = Text()
    for i, char in enumerate(text):
        pos = 0.3 * i + time_offset
        r = int(127 * (math.sin(pos) + 1))
        g = int(127 * (math.sin(pos + 2*math.pi/3) + 1))
        b = int(127 * (math.sin(pos + 4*math.pi/3) + 1))
        color_style = f"rgb({r},{g},{b})"
        rainbow_text.append(char, style=color_style)
    return rainbow_text

def create_rainbow_text(text):
    return create_rainbow_text_animated(text, 0)

def create_gradient_border():
    return "bright_red"

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

class ProxyManager:
    def __init__(self):
        self.config = load_config()
        self.proxies_db = {}
        self.load_database()
    
    def load_database(self):
        db_path = os.path.join(get_current_directory(), 'proxy_db.json')
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    self.proxies_db = json.load(f)
            except:
                self.proxies_db = {}
    
    def save_database(self):
        db_path = os.path.join(get_current_directory(), 'proxy_db.json')
        try:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(self.proxies_db, f, indent=4)
            return True
        except:
            return False
    
    def add_proxy(self, proxy_url, info):
        if proxy_url not in self.proxies_db:
            self.proxies_db[proxy_url] = {
                'added': datetime.now().isoformat(),
                'last_check': None,
                'checks': []
            }
        self.proxies_db[proxy_url].update(info)
        self.save_database()
    
    def get_proxy_info(self, proxy_url):
        return self.proxies_db.get(proxy_url, {})
    
    def update_proxy_check(self, proxy_url, check_result):
        if proxy_url in self.proxies_db:
            self.proxies_db[proxy_url]['last_check'] = datetime.now().isoformat()
            self.proxies_db[proxy_url]['checks'].append({
                'time': datetime.now().isoformat(),
                'result': check_result
            })
            if len(self.proxies_db[proxy_url]['checks']) > 10:
                self.proxies_db[proxy_url]['checks'] = self.proxies_db[proxy_url]['checks'][-10:]
            self.save_database()

    def get_favorites(self):
        return [p for p in self.proxies_db if p in self.config['favorite_proxies']]
    
    def add_to_favorites(self, proxy_url):
        if proxy_url not in self.config['favorite_proxies']:
            self.config['favorite_proxies'].append(proxy_url)
            save_config(self.config)
    
    def remove_from_favorites(self, proxy_url):
        if proxy_url in self.config['favorite_proxies']:
            self.config['favorite_proxies'].remove(proxy_url)
            save_config(self.config)
        
    def is_blacklisted(self, proxy_url):
        ip = proxy_url.split(':')[0]
        return ip in self.config['blacklisted_ips']
    
    def add_to_blacklist(self, proxy_url):
        ip = proxy_url.split(':')[0]
        if ip not in self.config['blacklisted_ips']:
            self.config['blacklisted_ips'].append(ip)
            save_config(self.config)

    def cleanup_old_records(self, days=30):
        cutoff = datetime.now() - timedelta(days=days)
        for proxy in list(self.proxies_db.keys()):
            last_check = self.proxies_db[proxy].get('last_check')
            if last_check:
                last_check = datetime.fromisoformat(last_check)
                if last_check < cutoff:
                    del self.proxies_db[proxy]
        self.save_database()

def center_text(text, width=80):
    return text.center(width)

def get_current_directory():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

reset = "\033[0m"

def get_yes_no_input(message):
    while True:
        choice = console.input(f"{message} [white]").strip().lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            console.print(f"[red]Vui lòng trả lời 'y' (có) hoặc 'n' (không)![/red]")



def get_default_config():
    return {
        'timeout': 10,
        'max_threads': 50,
        'test_urls': [
            {'url': 'http://www.google.com', 'weight': 1, 'timeout': 10, 'ssl': True},
            {'url': 'http://www.facebook.com', 'weight': 1, 'timeout': 10, 'ssl': True},
            {'url': 'http://www.youtube.com', 'weight': 2, 'timeout': 15, 'ssl': True}
        ],
        'check_levels': {
            'fast': {'max_tests': 2, 'min_speed': 1.0},
            'normal': {'max_tests': 3, 'min_speed': 2.0},
            'thorough': {'max_tests': 5, 'min_speed': 3.0}
        },
        'blacklisted_ips': [],
        'favorite_proxies': [],
        'last_update': None
    }

def save_config(config):
    config_path = os.path.join(get_current_directory(), 'config.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except:
        return False

async def ping_host(host):
    try:
        start_time = time.time()
        async with httpx.AsyncClient() as client:
            await client.head(f'http://{host}', timeout=5)
        return (time.time() - start_time) * 1000
    except:
        return None

class ProxyCollector:
    def __init__(self):
        self.sources = {
            'free-proxy-list': 'https://free-proxy-list.net/',
            'proxy-list': 'https://www.proxy-list.download/api/v1/get?type=http',
            'proxyscrape': 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http',
            'proxylist': 'https://www.proxy-list.download/api/v1/get?type=https'
        }
        
    async def collect_from_source(self, source_name, url):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    proxies = set()
                    for line in content.split('\n'):
                        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$', line.strip()):
                            proxies.add(line.strip())
                    return proxies
        except:
            return set()
        
    async def collect_all(self):
        tasks = []
        for source_name, url in self.sources.items():
            tasks.append(self.collect_from_source(source_name, url))
        
        results = await asyncio.gather(*tasks)
        all_proxies = set()
        for proxy_set in results:
            all_proxies.update(proxy_set)
        return list(all_proxies)

class ProxyChecker:
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager
        
    async def check_proxy(self, proxy_url, level='normal'):
        if self.proxy_manager.is_blacklisted(proxy_url):
            return {'url': proxy_url, 'status': 'blacklisted'}
        
        result = {
            'url': proxy_url,
            'status': 'unknown',
            'speed': 0,
            'latency': 0,
            'protocols': [],
            'is_private': None
        }
        
        try:
            ping_result = await asyncio.get_event_loop().run_in_executor(
                None, ping_host, proxy_url.split(':')[0]
            )
            
            if not ping_result:
                return {'url': proxy_url, 'status': 'failed', 'error': 'ping_failed'}
            
            result['latency'] = ping_result
            protocols = []
            
            for protocol in ['http', 'https', 'socks4', 'socks5']:
                try:
                    proxy_config = {protocol: f'{protocol}://{proxy_url}'}
                    async with httpx.AsyncClient(proxies=proxy_config, timeout=5) as client:
                        await client.head('http://www.google.com')
                        protocols.append(protocol)
                except:
                    continue
            
            result['protocols'] = protocols
            if not protocols:
                return {'url': proxy_url, 'status': 'failed', 'error': 'no_protocols'}
            
            level_config = self.proxy_manager.config['check_levels'][level]
            test_urls = self.proxy_manager.config['test_urls'][:level_config['max_tests']]
            speeds = []
            
            for test_url in test_urls:
                try:
                    proxy_config = {
                        'http': f'http://{proxy_url}',
                        'https': f'http://{proxy_url}'
                    }
                    
                    start_time = time.time()
                    async with httpx.AsyncClient(
                        proxies=proxy_config,
                        timeout=test_url['timeout'],
                        verify=test_url['ssl'],
                        http2=True,
                        limits=httpx.Limits(max_connections=5)
                    ) as client:
                        response = await client.get(test_url['url'])
                        if response.status_code == 200:
                            download_time = time.time() - start_time
                            content_length = int(response.headers.get('content-length', len(response.content)))
                            speed_mbps = (content_length * 8 / 1_000_000) / download_time
                            speeds.append({'speed': speed_mbps, 'weight': test_url['weight']})
                except:
                    continue
            
            if speeds:
                total_weight = sum(s['weight'] for s in speeds)
                weighted_speed = sum(s['speed'] * s['weight'] for s in speeds) / total_weight
                result['speed'] = round(weighted_speed, 2)
                result['status'] = 'working' if weighted_speed >= level_config['min_speed'] else 'slow'
            else:
                result['status'] = 'failed'
                result['error'] = 'speed_test_failed'
        
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        self.proxy_manager.update_proxy_check(proxy_url, result)
        return result
    
    async def check_proxies(self, proxy_list, level='normal'):
        semaphore = asyncio.Semaphore(self.proxy_manager.config['max_threads'])
        tasks = []
        
        async def bounded_check(proxy):
            async with semaphore:
                return await self.check_proxy(proxy, level)
        
        for proxy in proxy_list:
            tasks.append(bounded_check(proxy))
        
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn()
        ) as progress:
            task = progress.add_task("[cyan]Đang kiểm tra proxy...", total=len(tasks))
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.advance(task)
        
        return results

class ProxyRotator:
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager
        self.current_index = 0
        self.working_proxies = []
        self.update_working_proxies()
    
    def update_working_proxies(self):
        self.working_proxies = [
            proxy for proxy, info in self.proxy_manager.proxies_db.items()
            if info.get('last_check') and 
            datetime.fromisoformat(info['last_check']) > datetime.now() - timedelta(hours=1) and
            info['checks'][-1]['result']['status'] == 'working'
        ]
        random.shuffle(self.working_proxies)
    
    def get_next_proxy(self):
        if not self.working_proxies:
            self.update_working_proxies()
        if not self.working_proxies:
            return None
        
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        return proxy

async def check_proxy_protocols(proxy_url):
    protocols = []
    for protocol in ['http', 'https', 'socks4', 'socks5']:
        try:
            proxy_config = {
                'http://': f'{protocol}://{proxy_url}',
                'https://': f'{protocol}://{proxy_url}'
            }
            async with httpx.AsyncClient(proxies=proxy_config, timeout=5) as client:
                response = await client.head('https://www.google.com')
                if response.status_code == 200:
                    protocols.append(protocol)
        except:
            continue
    return protocols

async def is_private_proxy(proxy_url):
    try:
        ip = proxy_url.split(':')[0]
        async with httpx.AsyncClient() as client:
            response = await client.get(f'http://ip-api.com/json/{ip}', timeout=5)
            data = response.json()
            return data.get('hosting', False) or data.get('proxy', False)
    except:
        return None

def show_header():
    clear_screen()
    header_art = """
██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗    ███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗
██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝    ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝     ██╔████╔██║███████║███████╗   ██║   █████╗  ██████╔╝
██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝      ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗
██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║       ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

🌟🌟🌟 PROXY MASTER - ENTERPRISE EDITION 🌟🌟🌟
🚀 Made by: yeppp 🚀
    """
    lines = header_art.strip().split('\n')
    for line in lines:
        if line.strip():
            rainbow_line = create_rainbow_text(line)
            console.print(rainbow_line, justify="center")
        else:
            console.print()
    console.print()

def show_header_rich():
    show_header()

def check_and_install_dependencies():
    required_packages = {
        'httpx': 'httpx',
        'colorama': 'colorama',
        'aiohttp': 'aiohttp',
        'rich': 'rich',
        'psutil': 'psutil',
        'asyncio': 'asyncio'
    }
    
    console.print("[cyan]Checking dependencies...[/cyan]")
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
            console.print(f"[green]✓ {package} is installed[/green]")
        except ImportError:
            console.print(f"[yellow]Installing {package}...[/yellow]")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                console.print(f"[green]✓ Successfully installed {package}[/green]")
            except subprocess.CalledProcessError:
                console.print(f"[red]Failed to install {package}[/red]")
                sys.exit(1)
            
    console.print("[green]All dependencies are installed![/green]")

def select_proxy_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="CHỌN FILE PROXY CẦN CHECK",
        filetypes=[("Text files", "*.txt")]
    )
    root.destroy()
    return file_path

def validate_proxy_file(filename):
    try:
        with open(filename, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        if proxies:
            console.print(f"\n[green]✓ File hợp lệ! Tìm thấy {len(proxies)} proxy.[/green]")
            return True
        console.print(f"\n[red]✗ File không chứa proxy hợp lệ![/red]")
        return False
    except Exception:
        console.print(f"\n[red]✗ Không thể đọc file![/red]")
        return False

def validate_proxy_format(proxy):
    auth_pattern = r'^([^:]+):([^@]+)@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$'
    basic_pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$'

    auth_match = re.match(auth_pattern, proxy)
    if auth_match:
        ip_parts = auth_match.group(3).split('.')
        port = int(auth_match.group(4))
    else:
        basic_match = re.match(basic_pattern, proxy)
        if not basic_match:
            return False
        ip_parts = basic_match.group(1).split('.')
        port = int(basic_match.group(2))

    for part in ip_parts:
        if int(part) > 255:
            return False

    if port > 65535:
        return False

    return True

def parse_proxy_auth(proxy_url):
    if not proxy_url or not isinstance(proxy_url, str):
        return {'proxy': '', 'auth': None, 'has_auth': False, 'error': 'Invalid input'}
        
    try:
        clean_url = proxy_url
        original_protocol = None
        for protocol in ['http://', 'https://', 'socks4://', 'socks5://']:
            if clean_url.lower().startswith(protocol):
                original_protocol = protocol
                clean_url = clean_url[len(protocol):]
                break
        
        auth_pattern = r'^([^:]+):([^@]+)@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$'
        auth_match = re.match(auth_pattern, clean_url)

        if auth_match:
            username = auth_match.group(1)
            password = auth_match.group(2)
            ip = auth_match.group(3)
            port = auth_match.group(4)
            
            if not validate_ip(ip):
                return {'proxy': proxy_url, 'auth': None, 'has_auth': False, 'error': 'Invalid IP address'}
            if not validate_port(port):
                return {'proxy': proxy_url, 'auth': None, 'has_auth': False, 'error': 'Invalid port'}
                
            return {
                'proxy': f"{ip}:{port}",
                'auth': (username, password),
                'has_auth': True,
                'ip': ip,
                'port': port,
                'protocol': original_protocol or 'http://',
                'error': None
            }
            
        basic_pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$'
        basic_match = re.match(basic_pattern, clean_url)
        if basic_match:
            ip = basic_match.group(1)
            port = basic_match.group(2)
            
            if not validate_ip(ip):
                return {'proxy': proxy_url, 'auth': None, 'has_auth': False, 'error': 'Invalid IP address'}
            if not validate_port(port):
                return {'proxy': proxy_url, 'auth': None, 'has_auth': False, 'error': 'Invalid port'}
                
            return {
                'proxy': f"{ip}:{port}",
                'auth': None,
                'has_auth': False,
                'ip': ip,
                'port': port,
                'protocol': original_protocol or 'http://',
                'error': None
            }
            
    except (re.error, AttributeError) as e:
        return {'proxy': proxy_url, 'auth': None, 'has_auth': False, 'error': f'Parsing error: {str(e)}'}
        
    return {'proxy': proxy_url, 'auth': None, 'has_auth': False, 'error': 'Invalid proxy format'}

def validate_ip(ip):
    try:
        if not isinstance(ip, str):
            return False
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        return all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
    except (ValueError, AttributeError, TypeError):
        return False

def validate_port(port):
    try:
        port_num = int(port)
        return 0 < port_num <= 65535
    except (ValueError, TypeError):
        return False

def input_proxies_manually():
    console.print(f"\n[cyan]Nhập proxy thủ công[/cyan]")
    console.print(f"[yellow]Định dạng: ip:port (ví dụ: 127.0.0.1:8080)")
    console.print(f"Mỗi proxy trên một hàng, nhập xong nhấn Enter:[/yellow]")

    user_input = console.input(f"\n[white]").strip()

    if not user_input:
        console.print(f"\n[red]✗ Bạn chưa nhập proxy nào![/red]")
        return []

    lines = user_input.split('\n')
    proxies = []
    invalid_proxies = []

    for i, line in enumerate(lines, 1):
        proxy = line.strip()
        if proxy:
            if validate_proxy_format(proxy):
                proxies.append(proxy)
            else:
                invalid_proxies.append(f"Dòng {i}: {proxy}")

    if invalid_proxies:
        console.print(f"\n[red]✗ Các proxy không hợp lệ:[/red]")
        for invalid in invalid_proxies:
            console.print(f"[red]  - {invalid}[/red]")

        if proxies:
            console.print(f"\n[yellow]Tìm thấy {len(proxies)} proxy hợp lệ và {len(invalid_proxies)} proxy không hợp lệ.[/yellow]")
            continue_choice = get_yes_no_input(f"[cyan]Bạn muốn tiếp tục với các proxy hợp lệ? (y/n):[/cyan]")
            if not continue_choice:
                return []
        else:
            console.print(f"\n[red]Không có proxy hợp lệ nào![/red]")
            return []

    if proxies:
        console.print(f"\n[green]✓ Đã nhập thành công {len(proxies)} proxy hợp lệ:[/green]")
        for i, proxy in enumerate(proxies[:10], 1):
            console.print(f"[white]  {i}. {proxy}[/white]")

        if len(proxies) > 10:
            console.print(f"[yellow]  ... và {len(proxies) - 10} proxy khác[/yellow]")

        confirm = get_yes_no_input(f"\n[cyan]Xác nhận sử dụng các proxy này? (y/n):[/cyan]")
        if confirm:
            return proxies

    return []

async def test_proxy_security(proxy_url):
    if not proxy_url:
        return False, {'error': 'No proxy URL provided'}
    
    proxy_info = parse_proxy_auth(proxy_url)
    if not proxy_info['proxy'] or proxy_info.get('error'):
        return False, {'error': proxy_info.get('error', 'Invalid proxy format')}
        
    try:
        proxy_type = detect_proxy_type(proxy_url)
        security_results = {
            'ssl_verified': False,
            'dns_secure': False,
            'anonymous': False,
            'protocol': proxy_type,
            'encryption': None
        }
        
        if proxy_type == "https":
            ssl_test_urls = [
                "https://www.ssllabs.com/",
                "https://www.cloudflare.com/ssl/",
                "https://www.digicert.com/"
            ]
            
            for url in ssl_test_urls:
                try:
                    async with httpx.AsyncClient(
                        proxies={"https": proxy_url},
                        timeout=10,
                        verify=True,
                        http2=True
                    ) as client:
                        response = await client.get(url)
                        if response.status_code == 200:
                            security_results['ssl_verified'] = True
                            break
                except:
                    continue
        
        try:
            headers_test_url = "https://httpbin.org/headers"
            async with httpx.AsyncClient(
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=10
            ) as client:
                response = await client.get(headers_test_url)
                if response.status_code == 200:
                    headers = response.json().get('headers', {})
                    security_results['anonymous'] = not any(
                        header in headers for header in [
                            'X-Forwarded-For',
                            'Via',
                            'Forwarded',
                            'X-Real-IP'
                        ]
                    )
        except:
            pass
            
        return True, security_results
    except:
        return False, None

async def test_proxy_speed(proxy_url, test_size_mb=1, timeout=30):
    if not proxy_url:
        return 0, 0, {'error': 'No proxy URL provided'}
        
    speeds = []
    latencies = []
    weighted_total = 0
    total_weight = 0
    
    try:
        proxy_info = parse_proxy_auth(proxy_url)
        if not proxy_info['proxy'] or proxy_info.get('error'):
            return 0, 0, {'error': proxy_info.get('error', 'Invalid proxy format')}
            
        connectivity_url = 'http://www.google.com'
        try:
            async with httpx.AsyncClient(proxies={"http://": proxy_url}, timeout=5) as client:
                response = await client.head(connectivity_url)
                if response.status_code != 200:
                    return 0, 0, {'error': 'Proxy không thể kết nối'}
        except:
            return 0, 0, {'error': 'Proxy không phản hồi'}
            
        test_urls = [
            {
                'url': 'https://speed.cloudflare.com/__down?bytes=1048576',
                'weight': 3,
                'ssl': True,
                'timeout': 10
            },
            {
                'url': 'http://speedtest.ftp.otenet.gr/files/test1Mb.db',
                'weight': 2,
                'ssl': False,
                'timeout': 15
            },
            {
                'url': 'http://proof.ovh.net/files/1Mb.dat',
                'weight': 2,
                'ssl': False,
                'timeout': 15
            },
            {
                'url': 'http://speedtest-ny.turnkeyinternet.net/1mb.bin',
                'weight': 1,
                'ssl': False,
                'timeout': 20
            }
        ]
        
        proxy_type = detect_proxy_type(proxy_url)
        proxy_config = {}
        
        if proxy_info['has_auth']:
            auth_str = f"{proxy_info['auth'][0]}:{proxy_info['auth'][1]}@{proxy_info['proxy']}"
            if proxy_type == "socks4":
                proxy_config = {"socks4": f"socks4://{auth_str}"}
            elif proxy_type == "socks5":
                proxy_config = {"socks5": f"socks5://{auth_str}"}
            else:
                proxy_config = {
                    "http": f"http://{auth_str}",
                    "https": f"http://{auth_str}"
                }
        else:
            if proxy_type == "socks4":
                proxy_config = {"socks4": f"socks4://{proxy_info['proxy']}"}
            elif proxy_type == "socks5":
                proxy_config = {"socks5": f"socks5://{proxy_info['proxy']}"}
            else:
                proxy_config = {
                    "http": f"http://{proxy_info['proxy']}",
                    "https": f"http://{proxy_info['proxy']}"
                }
        
        test_urls.sort(key=lambda x: x['weight'], reverse=True)
        
        for test_config in test_urls:
            try:
                async with httpx.AsyncClient(
                    proxies=proxy_config,
                    timeout=test_config['timeout'],
                    verify=test_config['ssl'],
                    http2=True,
                    limits=httpx.Limits(
                        max_connections=5,
                        max_keepalive_connections=5,
                        keepalive_expiry=5.0
                    )
                ) as client:
                    start_time = time.time()
                    response = await client.get(test_config['url'])
                    if response.status_code == 200:
                        download_time = time.time() - start_time
                        content_length = int(response.headers.get('content-length', len(response.content)))
                        
                        speed_mbps = (content_length * 8 / 1_000_000) / download_time
                        
                        speeds.append({
                            'speed': speed_mbps,
                            'weight': test_config['weight']
                        })
                        latencies.append(download_time * 1000)
                        total_weight += test_config['weight']
                        if len(speeds) >= 3:
                            avg_speed = sum(s['speed'] for s in speeds) / len(speeds)
                            if avg_speed > 10 or len(speeds) >= 5:
                                break
            except (httpx.RequestError, httpx.TimeoutException) as e:
                continue
            except Exception as e:
                print(f"Lỗi trong quá trình kiểm tra tốc độ: {str(e)}")
                continue
                
        if speeds:
            weighted_speed = sum(s['speed'] * s['weight'] for s in speeds) / total_weight
            median_latency = sorted(latencies)[len(latencies) // 2]
            return round(weighted_speed, 2), round(median_latency, 2)
            
        return 0, 0
    except (httpx.RequestError, httpx.HTTPError) as e:
        return 0, 0
    except Exception as e:
        return 0, 0

class RateLimiter:
    def __init__(self, max_requests_per_second=10, burst_size=None):
        self.max_requests = max_requests_per_second
        self.burst_size = burst_size or max_requests_per_second * 2
        self.requests = []
        self.lock = threading.Lock()
        self.last_reset = time.time()
        self.total_requests = 0
        self.window_start = time.time()
        
    def reset_if_needed(self):
        now = time.time()
        if now - self.window_start >= 60:
            self.total_requests = 0
            self.window_start = now
            
    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            self.reset_if_needed()
            
            self.requests = [req_time for req_time in self.requests if now - req_time < 1.0]
            
            if len(self.requests) >= self.burst_size:
                sleep_time = 1.0 - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = time.time()
                    self.requests = [req_time for req_time in self.requests if now - req_time < 1.0]
            
            if len(self.requests) >= self.max_requests:
                sleep_time = 1.0 - (now - self.requests[-self.max_requests])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = time.time()
            
            self.requests.append(now)
            self.total_requests += 1

rate_limiter = RateLimiter(max_requests_per_second=15)

def test_proxy_enhanced(proxy_url, max_retries=3, rate_limiter=None):
    test_urls = [
        {
            "url": "http://ip-api.com/json",
            "ip_key": "query",
            "country_key": "countryCode",
            "timeout": 5,
            "weight": 1
        },
        {
            "url": "https://ipapi.co/json",
            "ip_key": "ip",
            "country_key": "country_code",
            "timeout": 6,
            "weight": 3
        },
        {
            "url": "https://httpbin.org/ip",
            "ip_key": "origin",
            "country_key": None,
            "timeout": 6,
            "weight": 2
        },
        {
            "url": "https://api.ipify.org?format=json",
            "ip_key": "ip",
            "country_key": None,
            "timeout": 5,
            "weight": 3
        },
        {
            "url": "https://ipinfo.io/json",
            "ip_key": "ip",
            "country_key": "country",
            "timeout": 7,
            "weight": 2
        }
    ]

    proxy_info = parse_proxy_auth(proxy_url)
    proxy = proxy_info['proxy']
    auth = proxy_info['auth']

    if proxy_url.startswith("socks4://"):
        proxy_config = {"socks4": f"socks4://{proxy}"}
    elif proxy_url.startswith("socks5://"):
        proxy_config = {"socks5": f"socks5://{proxy}"}
    else:
        if auth:
            proxy_with_auth = f"http://{auth[0]}:{auth[1]}@{proxy}"
            proxy_config = {"http": proxy_with_auth, "https": proxy_with_auth}
        else:
            proxy_config = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    results = []
    for attempt in range(max_retries + 1):
        weighted_urls = sorted(test_urls, key=lambda x: x["weight"] * random.uniform(0.8, 1.2), reverse=True)
        
        for test_config in weighted_urls:
            try:
                if rate_limiter:
                    rate_limiter.wait_if_needed()
                start_time = time.time()

                base_timeout = test_config["timeout"]
                timeout = get_dynamic_timeout(proxy_url, base_timeout, attempt)

                limits = httpx.Limits(
                    max_connections=200,
                    max_keepalive_connections=50,
                    keepalive_expiry=30.0)
                
                retry_strategy = httpx.RetryTransport(
                    max_retries=2,
                    max_backoff=10,
                    allowed_methods={"GET"}
                )

                with httpx.Client(
                    proxies=proxy_config,
                    timeout=timeout,
                    limits=limits,
                    transport=retry_strategy,
                    http2=True,
                    verify=True
                ) as client:
                    response = client.get(test_config["url"])

                response_time = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    data = response.json()
                    ip = data.get(test_config["ip_key"], "")

                    country = "?"
                    if test_config["country_key"] and test_config["country_key"] in data:
                        country = data[test_config["country_key"]]
                    elif ip:
                        country = get_country_from_ip(ip)

                    if ip:
                        results.append({
                            'ip': ip,
                            'country': country,
                            'response_time': response_time,
                            'weight': test_config['weight']
                        })

            except httpx.RequestError as e:
                if "timeout" in str(e).lower():
                    continue
                if attempt == max_retries:
                    print(f"Lỗi kết nối: {e}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [429, 403]:
                    continue
                if attempt == max_retries:
                    print(f"Lỗi HTTP {e.response.status_code}")
            except Exception as e:
                if attempt == max_retries:
                    print(f"Lỗi không xác định: {e}")
                continue

        if results:
            sorted_results = sorted(results, key=lambda x: (x['weight'], -x['response_time']), reverse=True)
            best_result = sorted_results[0]
            return best_result['ip'], best_result['country'], best_result['response_time']

        if attempt < max_retries:
            base_delay = 0.3 * (2 ** attempt)
            jitter = random.uniform(0, 0.2)
            time.sleep(base_delay + jitter)

    return None, None, 0

def detect_proxy_type(proxy_url):
    if not proxy_url or not isinstance(proxy_url, str):
        return "http"
    
    proxy_lower = proxy_url.lower()
    proxy_types = {
        "socks5://": "socks5",
        "socks4://": "socks4",
        "https://": "https"
    }
    
    for prefix, ptype in proxy_types.items():
        if proxy_lower.startswith(prefix):
            return ptype
            
    return "http"

def get_dynamic_timeout(proxy_url, base_timeout=5, attempt=0):
    proxy_type = detect_proxy_type(proxy_url)
    if proxy_type == "socks4":
        multiplier = 1.5
    elif proxy_type == "socks5":
        multiplier = 1.4
    elif proxy_type == "https":
        multiplier = 1.3
    else:
        multiplier = 1.2

    proxy_ip = proxy_url.split("://")[-1].split(":")[0]
    if proxy_ip.startswith(("1.", "8.", "208.")):
        region_multiplier = 1.0
    elif proxy_ip.startswith(("46.", "85.", "91.")):
        region_multiplier = 1.2
    elif proxy_ip.startswith(("103.", "118.", "202.")):
        region_multiplier = 1.5
    else:
        region_multiplier = 1.3

    attempt_multiplier = 1 + (attempt * 0.7)
    
    final_timeout = base_timeout * multiplier * region_multiplier * attempt_multiplier
    return min(final_timeout, 20)

def get_country_from_ip(ip):
    try:
        if ip.startswith("8.8.") or ip.startswith("1.1."):
            return "US"
        elif ip.startswith("208.67."):
            return "US"
        else:
            return "?"
    except:
        return "?"

def test_proxy(proxy_url):
    if not proxy_url:
        return None, None, None
        
    try:
        ip, country, response_time = test_proxy_enhanced(proxy_url)
        if ip and response_time >= 0:
            return ip, country or "?", response_time
    except Exception:
        pass
        
    return None, None, None

async def get_detailed_geolocation(ip):
    try:
        apis = [
            f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,city,isp,org,as,proxy,hosting",
            f"https://ipapi.co/{ip}/json/"
        ]

        async with httpx.AsyncClient(timeout=5) as client:
            for api_url in apis:
                try:
                    response = await client.get(api_url)
                    if response.status_code == 200:
                        data = response.json()

                        if "status" in data and data["status"] == "success":
                            return {
                                "country": data.get("country", "Unknown"),
                                "country_code": data.get("countryCode", "??"),
                                "city": data.get("city", "Unknown"),
                                "region": data.get("region", "Unknown"),
                                "isp": data.get("isp", "Unknown"),
                                "org": data.get("org", "Unknown"),
                                "is_proxy": data.get("proxy", False),
                                "is_hosting": data.get("hosting", False),
                                "anonymity": "Elite" if not data.get("proxy", False) else "Transparent"
                            }

                        elif "country_name" in data:
                            return {
                                "country": data.get("country_name", "Unknown"),
                                "country_code": data.get("country_code", "??"),
                                "city": data.get("city", "Unknown"),
                                "region": data.get("region", "Unknown"),
                                "isp": data.get("org", "Unknown"),
                                "org": data.get("org", "Unknown"),
                                "is_proxy": False,
                                "is_hosting": False,
                                "anonymity": "Anonymous"
                            }

                except Exception:
                    continue

        return {
            "country": "Unknown",
            "country_code": "??",
            "city": "Unknown",
            "region": "Unknown",
            "isp": "Unknown",
            "org": "Unknown",
            "is_proxy": False,
            "is_hosting": False,
            "anonymity": "Unknown"
        }

    except Exception:
        return None

def calculate_proxy_health_score(response_time, speed_mbps=0, anonymity="Unknown", is_hosting=False, error_count=0):
    if response_time <= 50:
        time_score = 50
    elif response_time <= 100:
        time_score = 40
    elif response_time <= 300:
        time_score = 30
    elif response_time <= 500:
        time_score = 20
    elif response_time <= 1000:
        time_score = 10
    else:
        time_score = max(0, 10 - (response_time - 1000) // 500)

    if speed_mbps >= 10:
        speed_score = 30
    elif speed_mbps >= 5:
        speed_score = 25
    elif speed_mbps >= 1:
        speed_score = 15
    elif speed_mbps >= 0.5:
        speed_score = 10
    else:
        speed_score = 5

    anonymity_scores = {
        "Elite": 25,
        "Anonymous": 20,
        "Transparent": 10,
        "Unknown": 15
    }
    anonymity_score = anonymity_scores.get(anonymity, 15)

    hosting_penalty = 15 if is_hosting else 0
    reliability_score = 15
    
    error_penalty = min(20, error_count * 5)
    stability_score = 10 if response_time < 1000 and speed_mbps > 1 else 0
    
    total_score = (
        time_score + 
        speed_score + 
        anonymity_score + 
        reliability_score + 
        stability_score - 
        hosting_penalty - 
        error_penalty
    )
    
    return max(0, min(100, total_score))

def analyze_proxy_stability(proxy_history):
    if not proxy_history:
        return 0
    
    total_checks = len(proxy_history)
    successful_checks = sum(1 for check in proxy_history if check['success'])
    avg_response_time = sum(check['response_time'] for check in proxy_history) / total_checks
    time_variance = sum((check['response_time'] - avg_response_time) ** 2 for check in proxy_history) / total_checks
    
    stability_score = (
        (successful_checks / total_checks) * 50 +
        (1 - min(time_variance / 1000000, 1)) * 30 +
        (1 - min(avg_response_time / 2000, 1)) * 20
    )
    
    return max(0, min(100, stability_score))

def get_health_score_color(score):
    if score >= 90:
        return "bright_cyan"
    elif score >= 80:
        return "bright_green"
    elif score >= 70:
        return "green"
    elif score >= 60:
        return "yellow"
    elif score >= 50:
        return "light_yellow"
    elif score >= 40:
        return "orange1"
    elif score >= 30:
        return "red"
    else:
        return "bright_red"

def get_health_score_emoji(score):
    if score >= 90:
        return "⭐"
    elif score >= 80:
        return "🟢"
    elif score >= 70:
        return "🟡"
    elif score >= 60:
        return "�"
    elif score >= 50:
        return "🟧"
    elif score >= 40:
        return "🟠"
    elif score >= 30:
        return "🔴"
    else:
        return "⛔"

def get_optimal_thread_count():
    import psutil
    
    cpu_count = psutil.cpu_count(logical=True)
    memory_gb = psutil.virtual_memory().total / (1024**3)
    memory_available_gb = psutil.virtual_memory().available / (1024**3)
    
    base_threads = cpu_count * 4
    
    memory_factor = min(1.0, memory_available_gb / (memory_gb * 0.4))
    
    if memory_gb < 4:
        base_threads = min(base_threads, 30)
    elif memory_gb < 8:
        base_threads = min(base_threads, 60)
    elif memory_gb < 16:
        base_threads = min(base_threads, 120)
    else:
        base_threads = min(base_threads, 250)
    
    cpu_usage = psutil.cpu_percent()
    if cpu_usage > 80:
        cpu_factor = 0.6
    elif cpu_usage > 60:
        cpu_factor = 0.8
    else:
        cpu_factor = 1.0
        
    optimal_threads = int(max(10, min(base_threads * memory_factor * cpu_factor, 300)))
    
    return optimal_threads

def select_optimal_test_server():
    test_servers = {
        'NA': [
            'http://speedtest-ny.turnkeyinternet.net/1mb.bin',
            'http://speedtest-la.turnkeyinternet.net/1mb.bin'
        ],
        'EU': [
            'http://speedtest.ftp.otenet.gr/files/test1Mb.db',
            'http://proof.ovh.net/files/1Mb.dat',
            'https://speed.hetzner.de/1GB.bin'
        ],
        'ASIA': [
            'https://files.arvancloud.com/download-test/1MB.test',
            'https://jp.download.test.com/1mb.bin'
        ]
    }
    
    min_latency = float('inf')
    best_servers = []
    
    for region, servers in test_servers.items():
        for server in servers:
            try:
                start_time = time.time()
                response = httpx.head(server, timeout=5)
                latency = time.time() - start_time
                
                if response.status_code == 200:
                    if latency < min_latency:
                        min_latency = latency
                        best_servers = [server]
                    elif latency == min_latency:
                        best_servers.append(server)
            except:
                continue
    
    return best_servers if best_servers else list(test_servers['EU'])

def monitor_system_performance():
    import psutil
    
    try:
        metrics = {
            "cpu_usage": psutil.cpu_percent(interval=0.5),
            "memory": psutil.virtual_memory(),
            "disk": psutil.disk_usage('/'),
            "network": psutil.net_io_counters()
        }
        
        performance_metrics = {
            "cpu_usage": metrics["cpu_usage"],
            "memory_usage": metrics["memory"].percent,
            "memory_available_gb": metrics["memory"].available / (1024 ** 3),
            "disk_usage": metrics["disk"].percent,
            "network_sent_mb": metrics["network"].bytes_sent / (1024 * 1024),
            "network_recv_mb": metrics["network"].bytes_recv / (1024 * 1024)
        }
        
        performance_metrics["high_load"] = (
            performance_metrics["cpu_usage"] > 80 or
            performance_metrics["memory_usage"] > 85 or
            performance_metrics["disk_usage"] > 90
        )
        
        if performance_metrics["memory_available_gb"] < 1:
            performance_metrics["high_load"] = True
            
        return performance_metrics
    except:
        return {
            "cpu_usage": 0,
            "memory_usage": 0,
            "memory_available_gb": 0,
            "disk_usage": 0,
            "network_sent_mb": 0,
            "network_recv_mb": 0,
            "high_load": False
        }

def adaptive_thread_adjustment(current_threads, performance_data):
    if performance_data["high_load"]:
        return max(10, int(current_threads * 0.7))
    elif performance_data["cpu_usage"] < 50 and performance_data["memory_usage"] < 60:
        return min(300, int(current_threads * 1.2))

    return current_threads

def apply_advanced_filters(proxy_results, config):
    filtered_results = []
    
    max_response_time = config.get("max_response_time", 1000)
    min_health_score = config.get("min_health_score", 60)
    blacklist_countries = set(config.get("blacklist_countries", []))
    preferred_countries = set(config.get("preferred_countries", []))
    preferred_anonymity = set(config.get("preferred_anonymity", []))
    exclude_hosting = config.get("exclude_hosting", False)
    min_speed = config.get("min_speed_mbps", 0.5)
    max_error_rate = config.get("max_error_rate", 0.3)
    
    for result in proxy_results:
        proxy, ip, country, response_time, geo_data, health_score = result
        
        if not ip or not country:
            continue
            
        if response_time > max_response_time:
            continue
            
        if health_score < min_health_score:
            continue
            
        if country in blacklist_countries:
            continue
            
        if preferred_countries and country not in preferred_countries:
            continue
            
        if geo_data:
            if "anonymity" in geo_data:
                if preferred_anonymity and geo_data["anonymity"] not in preferred_anonymity:
                    continue
                    
            if exclude_hosting and geo_data.get("is_hosting", False):
                continue
                
            if "speed_mbps" in geo_data and geo_data["speed_mbps"] < min_speed:
                continue
                
            if "error_rate" in geo_data and geo_data["error_rate"] > max_error_rate:
                continue
                
            proxy_type = detect_proxy_type(proxy)
            if config.get(f"exclude_{proxy_type}", False):
                continue
        
        filtered_results.append(result)
    
    return filtered_results

def sort_proxies_by_quality(proxy_results):
    return sorted(proxy_results, key=lambda x: (-x[5], x[3]))

def analyze_proxy_quality_trend(proxy_history):
    if not proxy_history or len(proxy_history) < 2:
        return 0, "stable"
    
    health_scores = []
    response_times = []
    
    for check in proxy_history:
        if isinstance(check, dict):
            if "health_score" in check and "response_time" in check:
                health_scores.append(check["health_score"])
                response_times.append(check["response_time"])
        elif hasattr(check, "health_score") and hasattr(check, "response_time"):
            health_scores.append(check.health_score)
            response_times.append(check.response_time)
            
    if not health_scores or not response_times:
        return 0, "stable"

    score_trend = sum(y - x for x, y in zip(health_scores, health_scores[1:])) / (len(health_scores) - 1)
    time_trend = sum(y - x for x, y in zip(response_times, response_times[1:])) / (len(response_times) - 1)
    
    if abs(score_trend) < 5 and abs(time_trend) < 50:
        trend = "stable"
    elif score_trend > 0 and time_trend < 0:
        trend = "improving"
    elif score_trend < 0 and time_trend > 0:
        trend = "degrading"
    else:
        trend = "fluctuating"
        
    reliability_score = (
        (1 - abs(score_trend) / 100) * 50 +
        (1 - abs(time_trend) / 1000) * 50
    )
    
    return reliability_score, trend

def categorize_proxies_by_performance(proxy_results):
    categories = {
        "premium": [],
        "good": [],
        "average": [],
        "poor": []
    }
    
    for result in proxy_results:
        proxy, ip, country, response_time, geo_data, health_score = result
        
        reliability_score = 0
        trend = "stable"
        
        if hasattr(result, "history"):
            reliability_score, trend = analyze_proxy_quality_trend(result.history)
        
        final_score = (health_score * 0.7 + reliability_score * 0.3)
        
        if final_score >= 80 and trend != "degrading":
            categories["premium"].append(result)
        elif final_score >= 60 or (trend == "improving" and final_score >= 50):
            categories["good"].append(result)
        elif final_score >= 40 or trend == "improving":
            categories["average"].append(result)
        else:
            categories["poor"].append(result)
    
    return categories

class ProxyAnalyticsDashboard:
    def __init__(self):
        self.stats = {
            "total_checked": 0,
            "live_proxies": 0,
            "dead_proxies": 0,
            "avg_response_time": 0,
            "countries": {},
            "anonymity_levels": {},
            "health_scores": [],
            "start_time": time.time()
        }

    def update_stats(self, proxy, ip, country, response_time, geo_data=None, health_score=0):
        self.stats["total_checked"] += 1

        if ip:
            self.stats["live_proxies"] += 1

            if country not in self.stats["countries"]:
                self.stats["countries"][country] = 0
            self.stats["countries"][country] += 1

            if geo_data and "anonymity" in geo_data:
                anonymity = geo_data["anonymity"]
                if anonymity not in self.stats["anonymity_levels"]:
                    self.stats["anonymity_levels"][anonymity] = 0
                self.stats["anonymity_levels"][anonymity] += 1

            self.stats["health_scores"].append(health_score)

            live_count = self.stats["live_proxies"]
            current_avg = self.stats["avg_response_time"]
            self.stats["avg_response_time"] = ((current_avg * (live_count - 1)) + response_time) / live_count

        else:
            self.stats["dead_proxies"] += 1

    def get_live_stats_panel(self):
        elapsed_time = time.time() - self.stats["start_time"]

        check_rate = self.stats["total_checked"] / elapsed_time if elapsed_time > 0 else 0
        success_rate = (self.stats["live_proxies"] / self.stats["total_checked"] * 100) if self.stats["total_checked"] > 0 else 0

        top_countries = sorted(self.stats["countries"].items(), key=lambda x: x[1], reverse=True)[:5]

        avg_health = sum(self.stats["health_scores"]) / len(self.stats["health_scores"]) if self.stats["health_scores"] else 0

        stats_content = f"""
[bold bright_cyan]📊 THỐNG KÊ REAL-TIME[/bold bright_cyan]

[bold bright_green]✅ Live:[/bold bright_green] {self.stats["live_proxies"]:,}
[bold bright_red]❌ Dead:[/bold bright_red] {self.stats["dead_proxies"]:,}
[bold bright_yellow]📈 Tỷ lệ thành công:[/bold bright_yellow] {success_rate:.1f}%
[bold bright_magenta]⚡ Tốc độ kiểm tra:[/bold bright_magenta] {check_rate:.1f} proxy/s
[bold bright_cyan]⏱️ Thời gian phản hồi TB:[/bold bright_cyan] {self.stats["avg_response_time"]:.0f}ms
[bold bright_white]🏥 Điểm sức khỏe TB:[/bold bright_white] {avg_health:.1f}/100

[bold bright_yellow]🌍 TOP QUỐC GIA:[/bold bright_yellow]
""" + "\n".join([f"  {country}: {count}" for country, count in top_countries[:3]])

        return Panel(
            stats_content,
            title="[bold bright_cyan]Analytics Dashboard[/bold bright_cyan]",
            border_style="bright_cyan",
            padding=(1, 2)
        )

print_lock = threading.Lock()

def create_rich_progress():
    return Progress(
        SpinnerColumn(spinner_style="bold bright_cyan"),
        TextColumn("[bold bright_magenta][progress.description]{task.description}"),
        BarColumn(bar_width=40, style="bright_green", complete_style="bright_cyan"),
        TaskProgressColumn(style="bold bright_yellow"),
        TimeElapsedColumn(style="bold bright_blue"),
        console=console
    )

def create_proxy_results_table(results):
    table = Table(title="🎯 Kết Quả Kiểm Tra Proxy", show_header=True, header_style="bold magenta")

    table.add_column("STT", style="dim", width=6, justify="center")
    table.add_column("Proxy", style="cyan", min_width=20)
    table.add_column("IP", style="green", min_width=15)
    table.add_column("Quốc Gia", style="yellow", width=10, justify="center")
    table.add_column("Ping", style="red", width=10, justify="center")
    table.add_column("Trạng Thái", width=12, justify="center")

    for i, (proxy, ip, country, response_time) in enumerate(results, 1):
        status = "[green]✅ LIVE[/green]"
        table.add_row(
            str(i),
            proxy,
            ip or "N/A",
            country or "?",
            f"{response_time}ms" if response_time else "N/A",
            status
        )

    return table

def create_enhanced_proxy_results_table(results):
    table = Table(title="🎯 Kết Quả Kiểm Tra Proxy Nâng Cao", show_header=True, header_style="bold magenta")

    table.add_column("STT", style="dim", width=6, justify="center")
    table.add_column("Proxy", style="cyan", min_width=20)
    table.add_column("IP", style="green", min_width=15)
    table.add_column("Quốc Gia", style="yellow", width=10, justify="center")
    table.add_column("Thành Phố", style="bright_blue", width=12, justify="center")
    table.add_column("Ping", style="red", width=8, justify="center")
    table.add_column("Sức Khỏe", style="bright_white", width=10, justify="center")
    table.add_column("Ẩn Danh", style="bright_magenta", width=12, justify="center")
    table.add_column("Trạng Thái", width=12, justify="center")

    for i, result in enumerate(results, 1):
        proxy, ip, country, response_time, geo_data, health_score = result

        city = geo_data.get('city', 'Unknown') if geo_data else 'Unknown'
        anonymity = geo_data.get('anonymity', 'Unknown') if geo_data else 'Unknown'

        health_emoji = get_health_score_emoji(health_score)
        health_color = get_health_score_color(health_score)
        health_display = f"{health_emoji}[{health_color}]{health_score}[/{health_color}]"

        anonymity_colors = {
            "Elite": "bright_green",
            "Anonymous": "yellow",
            "Transparent": "red",
            "Unknown": "dim"
        }
        anonymity_color = anonymity_colors.get(anonymity, "dim")
        anonymity_display = f"[{anonymity_color}]{anonymity}[/{anonymity_color}]"

        status = "[green]✅ LIVE[/green]"
        table.add_row(
            str(i),
            proxy,
            ip or "N/A",
            country or "?",
            city[:10] if city != 'Unknown' else "?",
            f"{response_time}ms" if response_time else "N/A",
            health_display,
            anonymity_display,
            status
        )

    return table

def show_proxy_statistics(total, live, dead):
    stats_table = Table(title="📊 Thống Kê Proxy", show_header=True, header_style="bold blue")

    stats_table.add_column("Loại", style="cyan", width=15)
    stats_table.add_column("Số Lượng", style="green", width=10, justify="center")
    stats_table.add_column("Tỷ Lệ", style="yellow", width=10, justify="center")

    live_rate = (live / total * 100) if total > 0 else 0
    dead_rate = (dead / total * 100) if total > 0 else 0

    stats_table.add_row("Tổng Proxy", f"{total:,}", "100%")
    stats_table.add_row("Proxy Sống", f"[green]{live:,}[/green]", f"[green]{live_rate:.1f}%[/green]")
    stats_table.add_row("Proxy Chết", f"[red]{dead:,}[/red]", f"[red]{dead_rate:.1f}%[/red]")

    console.print(stats_table)

def check_proxies_rich(proxies, classify, classify_type, output_path, max_threads):
    config = load_config()
    results = []
    live_proxies = []

    dashboard = ProxyAnalyticsDashboard()

    if config.get("enable_smart_threading", True):
        optimal_threads = get_optimal_thread_count()
        max_threads = min(max_threads, optimal_threads)
        console.print(f"[yellow]🧠 Smart Threading: Sử dụng {max_threads} threads (tối ưu: {optimal_threads})[/yellow]")

    classified_proxies = {
        "socks4": {},
        "socks5": {},
        "http": {},
        "https": {}
    }

    with create_rich_progress() as progress:
        task = progress.add_task("[cyan]Đang kiểm tra proxy...", total=len(proxies))

        async def process_proxy_rich_enhanced(proxy):
            ip, country, response_time = test_proxy(proxy)
            progress.advance(task)

            geo_data = None
            health_score = 0

            if ip:
                if config.get("enable_geolocation", True):
                    geo_data = await get_detailed_geolocation(ip)
                    if geo_data:
                        country = geo_data.get("country_code", country)

                if config.get("enable_health_scoring", True):
                    anonymity = geo_data.get("anonymity", "Unknown") if geo_data else "Unknown"
                    is_hosting = geo_data.get("is_hosting", False) if geo_data else False
                    health_score = calculate_proxy_health_score(response_time, 0, anonymity, is_hosting)

                dashboard.update_stats(proxy, ip, country, response_time, geo_data, health_score)

                result = (proxy, ip, country, response_time, geo_data, health_score)
                live_proxies.append(f"{proxy} | {response_time}ms | {health_score}/100")

                health_emoji = get_health_score_emoji(health_score)
                health_color = get_health_score_color(health_score)
                city_info = f" | {geo_data.get('city', 'Unknown')}" if geo_data else ""

                console.print(f"[green]✅ LIVE[/green] {proxy} | {ip} | {country}{city_info} | {response_time}ms | {health_emoji}[{health_color}]{health_score}[/{health_color}]")

                if classify:
                    proxy_type = "http"
                    if proxy.startswith("socks4://"):
                        proxy_type = "socks4"
                    elif proxy.startswith("socks5://"):
                        proxy_type = "socks5"
                    elif proxy.startswith("https://"):
                        proxy_type = "https"

                    if country not in classified_proxies[proxy_type]:
                        classified_proxies[proxy_type][country] = []
                    classified_proxies[proxy_type][country].append((proxy, response_time, health_score))

                return result
            else:
                dashboard.update_stats(proxy, None, None, 0)
                console.print(f"[red]❌ DEAD[/red] {proxy}")
                return None

        async def run_enhanced_checks():
            tasks = [process_proxy_rich_enhanced(proxy) for proxy in proxies]
            return await asyncio.gather(*tasks)

        enhanced_results = asyncio.run(run_enhanced_checks())
        results = list(filter(None, enhanced_results))

    console.print("\n")
    console.print(dashboard.get_live_stats_panel())

    if results and config.get("enable_advanced_filtering", True):
        console.print(f"\n[yellow]🔍 Áp dụng bộ lọc nâng cao...[/yellow]")
        filtered_results = apply_advanced_filters(results, config)
        console.print(f"[green]✅ Đã lọc: {len(filtered_results)}/{len(results)} proxy đạt tiêu chuẩn[/green]")
        results = filtered_results

    if results:
        results = sort_proxies_by_quality(results)
        console.print(f"[cyan]📊 Đã sắp xếp theo chất lượng[/cyan]")

    show_proxy_statistics(len(proxies), len(results), len(proxies) - len(results))

    if results:
        console.print("\n")

        categories = categorize_proxies_by_performance(results)
        console.print(f"[bold bright_green]🏆 Premium ({len(categories['premium'])})[/bold bright_green] | "
                     f"[bold bright_yellow]⭐ Good ({len(categories['good'])})[/bold bright_yellow] | "
                     f"[bold bright_orange1]📈 Average ({len(categories['average'])})[/bold bright_orange1] | "
                     f"[bold bright_red]📉 Poor ({len(categories['poor'])})[/bold bright_red]")

        results_table = create_enhanced_proxy_results_table(results[:10])
        console.print(results_table)

        if len(results) > 10:
            console.print(f"[yellow]... và {len(results) - 10} proxy khác[/yellow]")

    if results:
        enhanced_live_proxies = []
        for result in results:
            proxy, ip, country, response_time, geo_data, health_score = result
            city = geo_data.get('city', 'Unknown') if geo_data else 'Unknown'
            anonymity = geo_data.get('anonymity', 'Unknown') if geo_data else 'Unknown'
            enhanced_live_proxies.append(f"{proxy} | {response_time}ms | {health_score}/100 | {country} | {city} | {anonymity}")

        with open(output_path, "w", encoding='utf-8') as f:
            f.write('\n'.join(enhanced_live_proxies))

        if config.get("auto_bookmark_quality", True):
            auto_bookmark_quality_proxies(results)

        if config.get("auto_export_reports", True):
            export_detailed_reports(results, dashboard.stats, output_path)

        if classify:
            pass

    return results

def export_detailed_reports(results, stats, base_output_path):
    import csv
    from rich.console import Console
    from rich.table import Table
    from datetime import datetime
    import json
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = base_output_path.replace('.txt', '')

    json_report = {
        "timestamp": datetime.now().isoformat(),
        "summary": stats,
        "proxies": [],
        "performance_metrics": {
            "response_times": [],
            "health_scores": [],
            "countries": {},
            "proxy_types": {
                "http": 0,
                "https": 0,
                "socks4": 0,
                "socks5": 0
            }
        }
    }

    for result in results:
        proxy, ip, country, response_time, geo_data, health_score = result
        proxy_data = {
            "proxy": proxy,
            "ip": ip,
            "country": country,
            "response_time": response_time,
            "health_score": health_score,
            "geolocation": geo_data,
            "proxy_type": detect_proxy_type(proxy),
            "stability_score": analyze_proxy_stability([{"success": True, "response_time": response_time}])
        }
        json_report["proxies"].append(proxy_data)
        
        json_report["performance_metrics"]["response_times"].append(response_time)
        json_report["performance_metrics"]["health_scores"].append(health_score)
        json_report["performance_metrics"]["countries"][country] = json_report["performance_metrics"]["countries"].get(country, 0) + 1
        json_report["performance_metrics"]["proxy_types"][proxy_data["proxy_type"]] += 1

    json_file = f"{base_name}_report_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)

    csv_file = f"{base_name}_report_{timestamp}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Proxy', 'IP', 'Country', 'City', 'Response_Time', 'Health_Score', 'Anonymity', 'ISP'])

        for result in results:
            proxy, ip, country, response_time, geo_data, health_score = result
            city = geo_data.get('city', 'Unknown') if geo_data else 'Unknown'
            anonymity = geo_data.get('anonymity', 'Unknown') if geo_data else 'Unknown'
            isp = geo_data.get('isp', 'Unknown') if geo_data else 'Unknown'

            writer.writerow([proxy, ip, country, city, response_time, health_score, anonymity, isp])

    console.print(f"[green]📊 Đã xuất báo cáo: {json_file}, {csv_file}[/green]")

def manage_proxy_favorites():
    favorites_file = os.path.join(get_current_directory(), "proxy_favorites.json")

    def load_favorites():
        if os.path.exists(favorites_file):
            try:
                with open(favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_favorites(favorites):
        with open(favorites_file, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, indent=2, ensure_ascii=False)

    def add_to_favorites(proxy_data):
        favorites = load_favorites()
        for fav in favorites:
            if fav['proxy'] == proxy_data['proxy']:
                console.print(f"[yellow]⭐ Proxy {proxy_data['proxy']} đã có trong danh sách yêu thích[/yellow]")
                return

        favorites.append({
            **proxy_data,
            "added_date": datetime.now().isoformat(),
            "usage_count": 0
        })
        save_favorites(favorites)
        console.print(f"[green]⭐ Đã thêm {proxy_data['proxy']} vào danh sách yêu thích[/green]")

    def show_favorites():
        favorites = load_favorites()
        if not favorites:
            console.print("[yellow]📝 Chưa có proxy yêu thích nào[/yellow]")
            return

        table = Table(title="⭐ Proxy Yêu Thích", show_header=True, header_style="bold yellow")
        table.add_column("STT", width=6, justify="center")
        table.add_column("Proxy", style="cyan")
        table.add_column("Quốc Gia", style="yellow", width=10, justify="center")
        table.add_column("Sức Khỏe", style="green", width=10, justify="center")
        table.add_column("Ngày Thêm", style="dim", width=12)

        for i, fav in enumerate(favorites, 1):
            health_emoji = get_health_score_emoji(fav.get('health_score', 0))
            table.add_row(
                str(i),
                fav['proxy'],
                fav.get('country', '?'),
                f"{health_emoji}{fav.get('health_score', 0)}",
                fav.get('added_date', '')[:10]
            )

        console.print(table)

    return {
        'load': load_favorites,
        'save': save_favorites,
        'add': add_to_favorites,
        'show': show_favorites
    }

def auto_bookmark_quality_proxies(results):
    favorites_manager = manage_proxy_favorites()

    premium_proxies = [r for r in results if len(r) > 5 and r[5] >= 85]

    if premium_proxies:
        console.print(f"[yellow]⭐ Tự động bookmark {len(premium_proxies)} proxy chất lượng cao...[/yellow]")

        for result in premium_proxies:
            proxy, ip, country, response_time, geo_data, health_score = result
            proxy_data = {
                "proxy": proxy,
                "ip": ip,
                "country": country,
                "response_time": response_time,
                "health_score": health_score,
                "geolocation": geo_data
            }
            favorites_manager['add'](proxy_data)

def check_proxies(proxies, classify, classify_type, output_path, max_threads):
    results = []
    live_proxies = []

    classified_proxies = {
        "socks4": {},
        "socks5": {},
        "http": {},
        "https": {}
    }

    def process_proxy(proxy):
        ip, country, response_time = test_proxy(proxy)
        if ip:
            result = (proxy, ip, country, response_time)
            live_proxies.append(f"{proxy} | {response_time}ms")

            with print_lock:
                console.print(f"[green][LIVE] {proxy} | {ip} | {country} | {response_time}ms[/green]")

            if classify:
                proxy_type = "http"
                if proxy.startswith("socks4://"):
                    proxy_type = "socks4"
                elif proxy.startswith("socks5://"):
                    proxy_type = "socks5"
                elif proxy.startswith("https://"):
                    proxy_type = "https"

                if country not in classified_proxies[proxy_type]:
                    classified_proxies[proxy_type][country] = []
                classified_proxies[proxy_type][country].append((proxy, response_time))

            return result
        else:
            with print_lock:
                console.print(f"[red][DEAD] {proxy}[/red]")
            return None

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = list(filter(None, executor.map(process_proxy, proxies)))

    if not results:
        console.print(f"\n[red]✗ Không có proxy nào sống! Không có file nào được xuất ra.[/red]")
        return results

    with open(output_path, "a", encoding='utf-8') as f:
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            f.write("\n")
        f.write("\n".join(live_proxies))

    if classify:
        if classify_type == '1':
            country_file_path = os.path.join(get_current_directory(), "proxy_live_country.txt")
            with open(country_file_path, "a", encoding='utf-8') as f:
                if os.path.exists(country_file_path) and os.path.getsize(country_file_path) > 0:
                    f.write("\n")
                for proxy_type, countries in classified_proxies.items():
                    for country, proxy_list in countries.items():
                        if proxy_list:
                            f.write(f"{country}:\n")
                            for proxy, resp_time in proxy_list:
                                f.write(f"{proxy} | {resp_time}ms\n")
                            f.write("\n")
            console.print(f"[green]✓ Đã lưu proxy phân loại theo quốc gia: {country_file_path}[/green]")

        elif classify_type == '2':
            for proxy_type, countries in classified_proxies.items():
                proxy_list = []
                for country, plist in countries.items():
                    proxy_list.extend(plist)
                if proxy_list:
                    type_file_path = os.path.join(get_current_directory(), f"proxy_live_{proxy_type}.txt")
                    with open(type_file_path, "a", encoding='utf-8') as f:
                        if os.path.exists(type_file_path) and os.path.getsize(type_file_path) > 0:
                            f.write("\n")
                        f.write("\n".join([f"{proxy} | {resp_time}ms" for proxy, resp_time in proxy_list]))
                    console.print(f"[green]✓ Đã lưu proxy {proxy_type}: {type_file_path}[/green]")

        elif classify_type == '3':
            country_file_path = os.path.join(get_current_directory(), "proxy_live_country.txt")
            with open(country_file_path, "a", encoding='utf-8') as f:
                if os.path.exists(country_file_path) and os.path.getsize(country_file_path) > 0:
                    f.write("\n")
                for proxy_type, countries in classified_proxies.items():
                    for country, proxy_list in countries.items():
                        if proxy_list:
                            f.write(f"{country}:\n")
                            for proxy, resp_time in proxy_list:
                                f.write(f"{proxy} | {resp_time}ms\n")
                            f.write("\n")
            console.print(f"[green]✓ Đã lưu proxy phân loại theo quốc gia: {country_file_path}[/green]")

            for proxy_type, countries in classified_proxies.items():
                proxy_list = []
                for country, plist in countries.items():
                    proxy_list.extend(plist)
                if proxy_list:
                    type_file_path = os.path.join(get_current_directory(), f"proxy_live_{proxy_type}.txt")
                    with open(type_file_path, "a", encoding='utf-8') as f:
                        if os.path.exists(type_file_path) and os.path.getsize(type_file_path) > 0:
                            f.write("\n")
                        f.write("\n".join([f"{proxy} | {resp_time}ms" for proxy, resp_time in proxy_list]))
                    console.print(f"[green]✓ Đã lưu proxy {proxy_type}: {type_file_path}[/green]")

    return results

def show_loading_animation(message, stop_event):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = 0

    while not stop_event.is_set():
        with print_lock:
            spinner = chars[i % len(chars)]
            console.print(f"\r[bold bright_cyan]{message}[/bold bright_cyan] [bold bright_yellow]{spinner}[/bold bright_yellow]", end="")

        time.sleep(0.1)
        i += 1

    with print_lock:
        console.print(f"\r{' ' * (len(message) + 2)}\r", end="")

def show_rainbow_message(message, duration=1):
    rainbow_text = create_rainbow_text(message.strip())
    console.print(rainbow_text, justify="center")
    time.sleep(duration)

def show_success_animation(message):
    success_msg = f"✨ {message} ✨"
    rainbow_text = create_rainbow_text(success_msg)
    console.print(rainbow_text, justify="center")
    time.sleep(1)

def show_error_animation(message):
    error_msg = f"❌ {message} ❌"
    console.print(f"[bold bright_red]{error_msg}[/bold bright_red]", justify="center")
    time.sleep(1)

async def get_latest_commit_from_all_repos_async():
    repos = [
        "mzyui/proxy-list",
        "TheSpeedX/PROXY-List", 
        "roosterkid/openproxylist",
        "clarketm/proxy-list",
        "hookzof/socks5_list",
        "proxifly/free-proxy-list",
        "fate0/proxylist"
    ]
    
    latest_time = None
    
    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for repo in repos:
                url = f"https://api.github.com/repos/{repo}/commits?per_page=1"
                tasks.append(session.get(url, timeout=30))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for response in responses:
                try:
                    if not isinstance(response, Exception) and response.status == 200:
                        data = await response.json()
                        if data:
                            commit_date = data[0]['commit']['author']['date']
                            utc_time = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                            
                            if latest_time is None or utc_time > latest_time:
                                latest_time = utc_time
                except:
                    continue
    except:
        pass
    
    if latest_time:
        vn_time = latest_time + timedelta(hours=7)
        return vn_time.strftime("%Y-%m-%d %I:%M:%S %p (GMT+7)")
    
    return "Không xác định"

async def get_file_hash_async(url, session):
    try:
        async with session.head(url, timeout=30) as response:
            etag = response.headers.get('etag', '')
            last_modified = response.headers.get('last-modified', '')
            return hashlib.md5(f"{etag}{last_modified}".encode()).hexdigest()
    except:
        return None

def load_session_data():
    cache_file = os.path.join(get_current_directory(), "proxy_session_data.cache")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_session_data(data):
    cache_file = os.path.join(get_current_directory(), "proxy_session_data.cache")
    with open(cache_file, 'w') as f:
        json.dump(data, f)

def reset_session_data():
    cache_file = os.path.join(get_current_directory(), "proxy_session_data.cache")
    if os.path.exists(cache_file):
        os.remove(cache_file)

def load_config():
    config_file = os.path.join(get_current_directory(), "config.json")
    default_config = {
        "max_threads": 100,
        "timeout": 10,
        "preferred_countries": ["US", "UK", "DE", "FR"],
        "min_speed_mbps": 0.5,
        "use_rich_interface": True,
        "auto_save_results": True,
        "check_proxy_speed": False,
        "blacklist_countries": ["CN", "RU"],
        "retry_failed_proxies": True,
        "max_retries": 2,
        "min_health_score": 60,
        "max_response_time": 1000,
        "preferred_anonymity": ["Elite", "Anonymous"],
        "exclude_hosting": False,
        "min_uptime_percentage": 80,
        "enable_smart_threading": True,
        "enable_geolocation": True,
        "enable_health_scoring": True,
        "enable_advanced_filtering": True,
        "auto_export_reports": True,
        "auto_bookmark_quality": True,
        "rate_limit_requests_per_second": 15
    }

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except:
            return default_config
    else:
        save_config(default_config)
        return default_config

def save_config(config):
    config_file = os.path.join(get_current_directory(), "config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def show_country_list():
    countries_data = [
        ("AF", "Afghanistan"), ("AX", "Quần đảo Aland"), ("AL", "Albania"), ("DZ", "Algeria"),
        ("AS", "American Samoa"), ("AD", "Andorra"), ("AO", "Angola"), ("AI", "Anguilla"),
        ("AQ", "Nam Cực"), ("AG", "Antigua và Barbuda"), ("AR", "Argentina"), ("AM", "Armenia"),
        ("AW", "Aruba"), ("AU", "Châu Úc"), ("AT", "Áo"), ("AZ", "Azerbaijan"),
        ("BS", "Bahamas"), ("BH", "Bahrain"), ("BD", "Bangladesh"), ("BB", "Barbados"),
        ("BY", "Belarus"), ("BE", "Nước Bỉ"), ("BZ", "Belize"), ("BJ", "Bénin"),
        ("BM", "Bermuda"), ("BT", "Bhutan"), ("BO", "Bolivia"), ("BQ", "Bonaire"),
        ("BA", "Bosnia và Herzegovina"), ("BW", "Botswana"), ("BV", "Đảo Bouvet"), ("BR", "Brazil"),
        ("IO", "Lãnh thổ Anh tại Ấn Độ Dương"), ("BN", "Brunei"), ("BG", "Bulgaria"), ("BF", "Burkina Faso"),
        ("BI", "Burundi"), ("KH", "Campuchia"), ("CM", "Cameroon"), ("CA", "Canada"),
        ("CV", "Cape Verde"), ("KY", "Quần đảo Cayman"), ("CF", "Cộng hòa Trung Phi"), ("TD", "Chad"),
        ("CL", "Chile"), ("CN", "Trung Quốc"), ("CX", "Đảo Christmas"), ("CC", "Quần đảo Cocos"),
        ("CO", "Colombia"), ("KM", "Comoros"), ("CG", "Congo"), ("CD", "Congo Dân chủ"),
        ("CK", "Quần đảo Cook"), ("CR", "Costa Rica"), ("HR", "Croatia"), ("CW", "Curacao"),
        ("CY", "Síp"), ("CZ", "Séc"), ("DK", "Đan Mạch"), ("DJ", "Djibouti"),
        ("DM", "Dominica"), ("DO", "Cộng hòa Dominica"), ("EC", "Ecuador"), ("EG", "Ai Cập"),
        ("SV", "El Salvador"), ("GQ", "Equatorial Guinea"), ("ER", "Eritrea"), ("EE", "Estonia"),
        ("ET", "Ethiopia"), ("FK", "Quần đảo Falkland"), ("FO", "Quần đảo Faroe"), ("FJ", "Fiji"),
        ("FI", "Phần Lan"), ("FR", "Pháp"), ("GF", "Guiana thuộc Pháp"), ("PF", "French Polynesia"),
        ("TF", "Lãnh thổ phía Nam Pháp"), ("GA", "Gabon"), ("GM", "Gambia"), ("GE", "Georgia"),
        ("DE", "Nước Đức"), ("GH", "Ghana"), ("GI", "Gibraltar"), ("GR", "Hy Lạp"),
        ("GL", "Greenland"), ("GD", "Grenada"), ("GP", "Guadeloupe"), ("GU", "Guam"),
        ("GT", "Guatemala"), ("GG", "Guernsey"), ("GN", "Guinea"), ("GW", "Guinea-Bissau"),
        ("GY", "Guyana"), ("HT", "Haiti"), ("HM", "Đảo Heard"), ("VA", "Vatican"),
        ("HN", "Honduras"), ("HK", "Hồng Kông"), ("HU", "Hungary"), ("IS", "Iceland"),
        ("IN", "Ấn Độ"), ("ID", "Indonesia"), ("IQ", "Iraq"), ("IE", "Ireland"),
        ("IM", "Isle of Man"), ("IL", "Israel"), ("IT", "Italy"), ("JM", "Jamaica"),
        ("JP", "Nhật Bản"), ("JE", "Jersey"), ("JO", "Jordan"), ("KZ", "Kazakhstan"),
        ("KE", "Kenya"), ("KI", "Kiribati"), ("KR", "Hàn Quốc"), ("KW", "Kuwait"),
        ("KG", "Kyrgyzstan"), ("LA", "Lào"), ("LV", "Latvia"), ("LB", "Lebanon"),
        ("LS", "Lesotho"), ("LR", "Liberia"), ("LY", "Libya"), ("LI", "Liechtenstein"),
        ("LT", "Lithuania"), ("LU", "Luxembourg"), ("MO", "Macao"), ("MG", "Madagascar"),
        ("MW", "Malawi"), ("MY", "Malaysia"), ("MV", "Maldives"), ("ML", "Mali"),
        ("MT", "Malta"), ("MH", "Đảo Marshall"), ("MQ", "Martinique"), ("MR", "Mauritania"),
        ("MU", "Mauritius"), ("YT", "Mayotte"), ("MX", "Mexico"), ("FM", "Micronesia"),
        ("MD", "Moldova"), ("MC", "Monaco"), ("MN", "Mông Cổ"), ("ME", "Montenegro"),
        ("MS", "Montserrat"), ("MA", "Morocco"), ("MZ", "Mozambique"), ("MM", "Myanmar"),
        ("NA", "Namibia"), ("NR", "Nauru"), ("NP", "Nepal"), ("NL", "Hà Lan"),
        ("NC", "New Caledonia"), ("NZ", "New Zealand"), ("NI", "Nicaragua"), ("NE", "Niger"),
        ("NG", "Nigeria"), ("NU", "Niue"), ("NF", "Đảo Norfolk"), ("MK", "Bắc Macedonia"),
        ("MP", "Quần đảo Bắc Mariana"), ("NO", "Na Uy"), ("OM", "Oman"), ("PK", "Pakistan"),
        ("PW", "Palau"), ("PS", "Palestine"), ("PA", "Panama"), ("PG", "Papua New Guinea"),
        ("PY", "Paraguay"), ("PE", "Peru"), ("PH", "Philippines"), ("PN", "Pitcairn"),
        ("PL", "Ba Lan"), ("PT", "Bồ Đào Nha"), ("PR", "Puerto Rico"), ("QA", "Qatar"),
        ("RE", "Reunion"), ("RO", "Romania"), ("RU", "Nga"), ("RW", "Rwanda"),
        ("BL", "Saint Barthélemy"), ("SH", "Saint Helena"), ("KN", "Saint Kitts và Nevis"), ("LC", "Saint Lucia"),
        ("MF", "Saint Martin"), ("PM", "Saint Pierre"), ("VC", "Saint Vincent"), ("WS", "Samoa"),
        ("SM", "San Marino"), ("SA", "Ả Rập Saudi"), ("SN", "Senegal"), ("RS", "Serbia"),
        ("SC", "Seychelles"), ("SL", "Sierra Leone"), ("SG", "Singapore"), ("SX", "Sint Maarten"),
        ("SK", "Slovakia"), ("SI", "Slovenia"), ("SB", "Quần đảo Solomon"), ("SO", "Somalia"),
        ("ZA", "Nam Phi"), ("GS", "Nam Georgia"), ("SS", "Nam Sudan"), ("ES", "Tây Ban Nha"),
        ("LK", "Sri Lanka"), ("SR", "Suriname"), ("SD", "Sudan"), ("SJ", "Svalbard"),
        ("SE", "Thụy Điển"), ("CH", "Thụy Sĩ"), ("ST", "São Tomé"), ("TW", "Đài Loan"),
        ("TJ", "Tajikistan"), ("TZ", "Tanzania"), ("TH", "Thái Lan"), ("TG", "Togo"),
        ("TK", "Tokelau"), ("TO", "Tonga"), ("TT", "Trinidad và Tobago"), ("TN", "Tunisia"),
        ("TR", "Thổ Nhĩ Kỳ"), ("TM", "Turkmenistan"), ("TC", "Turks và Caicos"), ("TV", "Tuvalu"),
        ("UG", "Uganda"), ("UA", "Ukraine"), ("AE", "UAE"), ("GB", "Anh"),
        ("US", "Hoa Kỳ"), ("UM", "Tiểu đảo Hoa Kỳ"), ("UY", "Uruguay"), ("UZ", "Uzbekistan"),
        ("VU", "Vanuatu"), ("VE", "Venezuela"), ("VN", "Việt Nam"), ("VG", "Virgin Islands Anh"),
        ("VI", "Virgin Islands Mỹ"), ("WF", "Wallis và Futuna"), ("EH", "Tây Sahara"), ("YE", "Yemen"),
        ("ZM", "Zambia"), ("ZW", "Zimbabwe")
    ]

    countries = {}
    for i, (code, name) in enumerate(countries_data, 1):
        countries[str(i)] = f"{code}: {name}"

    title = create_rainbow_text("🌍 DANH SÁCH TẤT CẢ MÃ KHU VỰC TRÊN THẾ GIỚI 🌍")

    table = Table(
        title=title,
        show_header=True,
        header_style="bold bright_magenta",
        border_style=create_gradient_border(),
        title_style="bold",
        caption="💡 Chọn số hoặc nhập trực tiếp mã (VD: 1,2,3 hoặc US,VN,JP)",
        caption_style="italic bright_yellow",
        expand=True,
        show_lines=True
    )

    table.add_column("STT", style="bold bright_red", width=4, justify="center")
    table.add_column("MÃ", style="bold bright_green", width=4, justify="center")
    table.add_column("TÊN KHU VỰC", style="bold bright_cyan", width=18)
    table.add_column("STT", style="bold bright_red", width=4, justify="center")
    table.add_column("MÃ", style="bold bright_green", width=4, justify="center")
    table.add_column("TÊN KHU VỰC", style="bold bright_cyan", width=18)
    table.add_column("STT", style="bold bright_red", width=4, justify="center")
    table.add_column("MÃ", style="bold bright_green", width=4, justify="center")
    table.add_column("TÊN KHU VỰC", style="bold bright_cyan", width=18)
    table.add_column("STT", style="bold bright_red", width=4, justify="center")
    table.add_column("MÃ", style="bold bright_green", width=4, justify="center")
    table.add_column("TÊN KHU VỰC", style="bold bright_cyan", width=18)

    def format_country(code, name):
        formatted_code = f"[bright_cyan]{code}[/bright_cyan]"
        formatted_name = f"[white]{name}[/white]"
        return formatted_code, formatted_name

    for i in range(0, len(countries_data), 4):
        row_data = []

        for j in range(4):
            if i + j < len(countries_data):
                data = countries_data[i + j]
                stt = str(i + j + 1)
                code, name = format_country(data[0], data[1])
                row_data.extend([stt, code, name])
            else:
                row_data.extend(["", "", ""])

        table.add_row(*row_data)

    console.print("\n")
    console.print(table)
    console.print(f"\n[bold bright_green]✨ Tổng cộng: {len(countries_data)} khu vực trên toàn thế giới ✨[/bold bright_green]")

    return countries

def ask_use_config():
    config = load_config()

    console.print("\n")
    console.print(Panel(
        Text("⚙️ SỬ DỤNG CẤU HÌNH ĐÃ LƯU", style="bold bright_yellow") + "\n\n" +
        Text("Bạn có muốn sử dụng cấu hình đã lưu không?", style="bright_white") + "\n\n" +
        Text("Cấu hình hiện tại:", style="bright_cyan") + "\n" +
        Text(f"• Số luồng: {config['max_threads']}", style="white") + "\n" +
        Text(f"• Thời gian chờ: {config['timeout']}s", style="white") + "\n" +
        Text(f"• Giao diện Rich: {'Bật' if config['use_rich_interface'] else 'Tắt'}", style="white") + "\n" +
        Text(f"• Tự động lưu: {'Bật' if config['auto_save_results'] else 'Tắt'}", style="white") + "\n\n" +
        Text("💡 Chọn 'y' để dùng config, 'n' để tùy chỉnh lại", style="italic bright_green"),
        title="[bold bright_blue]🔧 CẤU HÌNH[/bold bright_blue]",
        border_style="bright_blue",
        padding=(1, 2)
    ))

    choice = console.input("\n[bold bright_cyan]Sử dụng cấu hình đã lưu? (y/n): [/bold bright_cyan]").strip().lower()
    return choice == 'y', config

def get_user_settings(use_config, config):
    settings = {}

    if use_config:
        settings = {
            'max_threads': config['max_threads'],
            'timeout': config['timeout'],
            'use_rich_interface': config['use_rich_interface'],
            'auto_save_results': config['auto_save_results'],
            'check_proxy_speed': config.get('check_proxy_speed', False)
        }
        console.print(f"[green]✅ Đang sử dụng cấu hình đã lưu[/green]")
    else:
        console.print(f"[yellow]⚙️ Tùy chỉnh cấu hình mới[/yellow]")

        while True:
            try:
                max_threads = int(console.input("[bold bright_cyan]◆ Nhập số luồng (tối thiểu 1): [/bold bright_cyan]"))
                if max_threads >= 1:
                    settings['max_threads'] = max_threads
                    break
                console.print("[bold bright_red]◆ Số luồng phải lớn hơn 0 ◆[/bold bright_red]")
            except ValueError:
                console.print("[bold bright_red]◆ Vui lòng nhập số hợp lệ ◆[/bold bright_red]")

        while True:
            try:
                timeout = int(console.input("[bold bright_cyan]◆ Nhập thời gian chờ (giây, tối thiểu 1): [/bold bright_cyan]"))
                if timeout >= 1:
                    settings['timeout'] = timeout
                    break
                console.print("[bold bright_red]◆ Thời gian chờ phải lớn hơn 0 giây ◆[/bold bright_red]")
            except ValueError:
                console.print("[bold bright_red]◆ Vui lòng nhập số hợp lệ ◆[/bold bright_red]")

        settings['use_rich_interface'] = console.input("[bold bright_cyan]◆ Sử dụng giao diện Rich? (y/n): [/bold bright_cyan]").strip().lower() == 'y'
        settings['auto_save_results'] = console.input("[bold bright_cyan]◆ Tự động lưu kết quả? (y/n): [/bold bright_cyan]").strip().lower() == 'y'
        settings['check_proxy_speed'] = console.input("[bold bright_cyan]◆ Kiểm tra tốc độ proxy? (y/n): [/bold bright_cyan]").strip().lower() == 'y'

        save_choice = console.input("\n[bold bright_yellow]💾 Lưu cấu hình này cho lần sau? (y/n): [/bold bright_yellow]").strip().lower()
        if save_choice == 'y':
            new_config = config.copy()
            new_config.update(settings)
            save_config(new_config)
            console.print("[green]✅ Đã lưu cấu hình thành công![/green]")

    return settings

def show_config_menu():
    config = load_config()

    while True:
        clear_screen()
        show_header_rich() if config.get('use_rich_interface', True) else show_header()

        config_title = create_rainbow_text("◆◆◆ BẢNG ĐIỀU KHIỂN CẤU HÌNH HỆ THỐNG ◆◆◆")

        console.print(Panel(
            config_title + "\n\n" +
            Text("🤔 CẤU HÌNH HỆ THỐNG LÀ GÌ?", style="bold bright_yellow") + "\n" +
            Text("Đây là nơi bạn có thể tùy chỉnh cách tool hoạt động:", style="bright_white") + "\n" +
            Text("• Số luồng: Bao nhiêu proxy kiểm tra cùng lúc (không giới hạn, tùy máy)", style="dim") + "\n" +
            Text("• Thời gian chờ: Chờ bao lâu trước khi bỏ qua proxy chậm (không giới hạn)", style="dim") + "\n" +
            Text("• Giao diện Rich: Bật/tắt màu sắc đẹp", style="dim") + "\n" +
            Text("• Tự động lưu: Tự động lưu kết quả ra file", style="dim") + "\n" +
            Text("💡 Mẹo: Máy xịn thì để số luồng cao, cấu hình 1 lần dùng mãi!", style="italic bright_green") + "\n\n" +
            Text("「 Tham số hệ thống nâng cao 」", style="italic bright_white") + "\n\n" +
            Text("【 1 】", style="bold red on black") + Text(f" Số luồng: ", style="bright_white") + Text(f"{config['max_threads']}", style="bold green") + "\n" +
            Text("【 2 】", style="bold orange1 on black") + Text(f" Thời gian chờ: ", style="bright_white") + Text(f"{config['timeout']}s", style="bold green") + "\n" +
            Text("【 3 】", style="bold yellow on black") + Text(f" Tốc độ tối thiểu: ", style="bright_white") + Text(f"{config['min_speed_mbps']} Mbps", style="bold green") + "\n" +
            Text("【 4 】", style="bold green on black") + Text(f" Giao diện Rich: ", style="bright_white") + Text(f"{'Bật' if config['use_rich_interface'] else 'Tắt'}", style="bold green") + "\n" +
            Text("【 5 】", style="bold cyan on black") + Text(f" Tự động lưu: ", style="bright_white") + Text(f"{'Bật' if config['auto_save_results'] else 'Tắt'}", style="bold green") + "\n" +
            Text("【 6 】", style="bold blue on black") + Text(f" Kiểm tra tốc độ: ", style="bright_white") + Text(f"{'Bật' if config['check_proxy_speed'] else 'Tắt'}", style="bold green") + "\n" +
            Text("【 7 】", style="bold magenta on black") + Text(f" Khu vực ưu tiên: ", style="bright_white") + Text(f"{', '.join(config['preferred_countries'])}", style="bold green") + "\n" +
            Text("【 8 】", style="bold purple on black") + Text(f" Khu vực chặn: ", style="bright_white") + Text(f"{', '.join(config['blacklist_countries'])}", style="bold green") + "\n\n" +
            Text("【 9 】", style="bold bright_green on black") + Text(" Lưu và thoát", style="bright_green") + "\n" +
            Text("⓪", style="bold bright_red") + Text(" Thoát không lưu", style="bright_red"),
            border_style=create_gradient_border(),
            padding=(2, 4),
            title="[bold bright_cyan]◆ BỘ CẤU HÌNH ◆[/bold bright_cyan]",
            title_align="center"
        ), justify="center")

        choice = console.input("\n[bold bright_cyan]◆ Chọn tham số để chỉnh sửa (0-9): [/bold bright_cyan]").strip()

        if choice == '1':
            try:
                new_threads = int(console.input("[bold bright_cyan]◆ Nhập số luồng mới (tối thiểu 1): [/bold bright_cyan]"))
                if new_threads >= 1:
                    config['max_threads'] = new_threads
                    console.print("[bold bright_green]◆ Cấu hình đã cập nhật thành công ◆[/bold bright_green]")
                else:
                    console.print("[bold bright_red]◆ Số luồng phải lớn hơn 0 ◆[/bold bright_red]")
            except ValueError:
                console.print("[bold bright_red]◆ Định dạng đầu vào không hợp lệ ◆[/bold bright_red]")
            time.sleep(1)

        elif choice == '2':
            try:
                new_timeout = int(console.input("[bold bright_cyan]◆ Nhập thời gian chờ mới (giây, tối thiểu 1): [/bold bright_cyan]"))
                if new_timeout >= 1:
                    config['timeout'] = new_timeout
                    console.print("[bold bright_green]◆ Cấu hình thời gian chờ đã cập nhật ◆[/bold bright_green]")
                else:
                    console.print("[bold bright_red]◆ Thời gian chờ phải lớn hơn 0 giây ◆[/bold bright_red]")
            except ValueError:
                console.print("[bold bright_red]◆ Giá trị thời gian chờ không hợp lệ ◆[/bold bright_red]")
            time.sleep(1)

        elif choice == '3':
            try:
                new_speed = float(console.input("[bold bright_cyan]◆ Nhập tốc độ tối thiểu mới (Mbps, tối thiểu 0.1): [/bold bright_cyan]"))
                if new_speed >= 0.1:
                    config['min_speed_mbps'] = new_speed
                    console.print("[bold bright_green]◆ Cấu hình tốc độ tối thiểu đã cập nhật ◆[/bold bright_green]")
                else:
                    console.print("[bold bright_red]◆ Tốc độ tối thiểu phải lớn hơn 0.1 Mbps ◆[/bold bright_red]")
            except ValueError:
                console.print("[bold bright_red]◆ Giá trị tốc độ không hợp lệ ◆[/bold bright_red]")
            time.sleep(1)

        elif choice == '4':
            config['use_rich_interface'] = not config['use_rich_interface']
            status = "Bật" if config['use_rich_interface'] else "Tắt"
            console.print(f"[bold bright_green]◆ Giao diện Rich đã {status} ◆[/bold bright_green]")
            time.sleep(1)

        elif choice == '5':
            config['auto_save_results'] = not config['auto_save_results']
            status = "Bật" if config['auto_save_results'] else "Tắt"
            console.print(f"[bold bright_green]◆ Tự động lưu đã {status} ◆[/bold bright_green]")
            time.sleep(1)

        elif choice == '6':
            config['check_proxy_speed'] = not config['check_proxy_speed']
            status = "Bật" if config['check_proxy_speed'] else "Tắt"
            console.print(f"[bold bright_green]◆ Kiểm tra tốc độ đã {status} ◆[/bold bright_green]")
            time.sleep(1)

        elif choice == '7':
            console.print("\n[bold bright_yellow]◆ Chỉnh sửa khu vực ưu tiên ◆[/bold bright_yellow]")
            console.print(f"[dim]Hiện tại: {', '.join(config['preferred_countries'])}[/dim]")

            show_list = console.input("[bold bright_cyan]◆ Hiển thị danh sách mã khu vực? (y/n): [/bold bright_cyan]").strip().lower()
            if show_list == 'y':
                countries = show_country_list()
                choice_input = console.input("[bold bright_cyan]◆ Chọn số hoặc nhập mã (VD: 1,2,3 hoặc US,UK,DE): [/bold bright_cyan]").strip()

                if choice_input.replace(',', '').replace(' ', '').isdigit():
                    selected_codes = []
                    for num in choice_input.split(','):
                        num = num.strip()
                        if num in countries:
                            code = countries[num].split(':')[0]
                            selected_codes.append(code)
                    if selected_codes:
                        config['preferred_countries'] = selected_codes
                        console.print(f"[bold bright_green]◆ Đã cập nhật: {', '.join(selected_codes)} ◆[/bold bright_green]")
                else:
                    config['preferred_countries'] = [c.strip().upper() for c in choice_input.split(',') if c.strip()]
                    console.print(f"[bold bright_green]◆ Đã cập nhật: {', '.join(config['preferred_countries'])} ◆[/bold bright_green]")
            else:
                new_countries = console.input("[bold bright_cyan]◆ Nhập mã khu vực (để trống = không thay đổi): [/bold bright_cyan]").strip()
                if new_countries:
                    config['preferred_countries'] = [c.strip().upper() for c in new_countries.split(',') if c.strip()]
                    console.print(f"[bold bright_green]◆ Đã cập nhật: {', '.join(config['preferred_countries'])} ◆[/bold bright_green]")
                else:
                    console.print("[bold bright_yellow]◆ Không có thay đổi ◆[/bold bright_yellow]")
            time.sleep(1)

        elif choice == '8':
            console.print("\n[bold bright_yellow]◆ Chỉnh sửa khu vực chặn ◆[/bold bright_yellow]")
            console.print(f"[dim]Hiện tại: {', '.join(config['blacklist_countries'])}[/dim]")

            show_list = console.input("[bold bright_cyan]◆ Hiển thị danh sách mã khu vực? (y/n): [/bold bright_cyan]").strip().lower()
            if show_list == 'y':
                countries = show_country_list()
                choice_input = console.input("[bold bright_cyan]◆ Chọn số hoặc nhập mã (VD: 1,2,3 hoặc US,UK,DE): [/bold bright_cyan]").strip()

                if choice_input.replace(',', '').replace(' ', '').isdigit():
                    selected_codes = []
                    for num in choice_input.split(','):
                        num = num.strip()
                        if num in countries:
                            code = countries[num].split(':')[0]
                            selected_codes.append(code)
                    if selected_codes:
                        config['blacklist_countries'] = selected_codes
                        console.print(f"[bold bright_green]◆ Đã cập nhật: {', '.join(selected_codes)} ◆[/bold bright_green]")
                else:
                    config['blacklist_countries'] = [c.strip().upper() for c in choice_input.split(',') if c.strip()]
                    console.print(f"[bold bright_green]◆ Đã cập nhật: {', '.join(config['blacklist_countries'])} ◆[/bold bright_green]")
            else:
                new_countries = console.input("[bold bright_cyan]◆ Nhập mã khu vực (để trống = không thay đổi): [/bold bright_cyan]").strip()
                if new_countries:
                    config['blacklist_countries'] = [c.strip().upper() for c in new_countries.split(',') if c.strip()]
                    console.print(f"[bold bright_green]◆ Đã cập nhật: {', '.join(config['blacklist_countries'])} ◆[/bold bright_green]")
                else:
                    console.print("[bold bright_yellow]◆ Không có thay đổi ◆[/bold bright_yellow]")
            time.sleep(1)

        elif choice == '9':
            save_config(config)
            console.print("[bold bright_green]◆ Cấu hình đã được lưu thành công ◆[/bold bright_green]")
            time.sleep(1)
            break

        elif choice == '0':
            console.print("[bold bright_yellow]◆ Thoát mà không lưu thay đổi ◆[/bold bright_yellow]")
            time.sleep(1)
            break

        else:
            console.print("[bold bright_red]◆ Lựa chọn không hợp lệ ◆[/bold bright_red]")
            time.sleep(1)

def rotate_sources(sources, rotation_key="default"):
    current_hour = int(time.time() // 3600)
    seed = hashlib.md5(f"{rotation_key}_{current_hour}".encode()).hexdigest()
    rotation_offset = int(seed[:8], 16) % len(sources)
    return sources[rotation_offset:] + sources[:rotation_offset]

def get_proxy_urls_with_rotation():
    base_urls = get_proxy_urls_static()
    rotated_urls = {}
    for category, urls in base_urls.items():
        rotated_urls[category] = rotate_sources(urls, f"proxy_{category}")
    return rotated_urls

def get_proxy_urls_static():
    return {
        'all': [
            'https://raw.githubusercontent.com/mzyui/proxy-list/refs/heads/main/all.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS.txt',
            'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4.txt',
            'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5.txt',
            'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
            'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all.txt',
            'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
            'https://vakhov.github.io/fresh-proxy-list/proxylist.txt',
            'https://raw.githubusercontent.com/antoinevastel/avastel-bot-ips-lists/master/avastel-proxy-bot-ips-1day.txt',
            'https://raw.githubusercontent.com/antoinevastel/avastel-bot-ips-lists/master/avastel-proxy-bot-ips-blocklist-5days.txt',
            'https://raw.githubusercontent.com/antoinevastel/avastel-bot-ips-lists/master/avastel-proxy-bot-ips-blocklist-8days.txt',
            'https://raw.githubusercontent.com/FifzzSENZE/Master-Proxy/master/proxies/all.txt',
            'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt',
            'https://raw.githubusercontent.com/prxchk/proxy-list/main/all.txt',
            'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/proxy.txt',
            'https://raw.githubusercontent.com/almroot/proxylist/master/list.txt',
            'https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt',
            'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt',
            'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/all.txt',
            'API_PROXYSCRAPE',
            'API_GEONODE',
            'API_PROXYLIST',
            'API_FREEPROXY',
            'API_PROXYNOVA',
            'API_SPYSONE',
            'API_PROXYSCAN',
            'API_PROXYROTATOR',
            'API_PROXYHUB',
            'API_PROXYSPACE'
        ],
        'http': [
            'https://raw.githubusercontent.com/mzyui/proxy-list/refs/heads/main/http.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://vakhov.github.io/fresh-proxy-list/http.txt',
            'https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/http.txt',
            'https://raw.githubusercontent.com/FifzzSENZE/Master-Proxy/master/proxies/http.txt',
            'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt',
            'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt',
            'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt',
            'API_PROXYSCRAPE',
            'API_GEONODE',
            'API_PROXYLIST',
            'API_FREEPROXY'
        ],
        'https': [
            'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS.txt',
            'https://vakhov.github.io/fresh-proxy-list/https.txt',
            'https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/https.txt',
            'https://raw.githubusercontent.com/FifzzSENZE/Master-Proxy/master/proxies/https.txt',
            'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/https/data.txt',
            'https://raw.githubusercontent.com/mzyui/proxy-list/refs/heads/main/https.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'API_PROXYSCRAPE',
            'API_GEONODE',
            'API_PROXYNOVA',
            'API_SPYSONE'
        ],
        'socks4': [
            'https://raw.githubusercontent.com/mzyui/proxy-list/refs/heads/main/socks4.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
            'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4.txt',
            'https://vakhov.github.io/fresh-proxy-list/socks4.txt',
            'https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks4.txt',
            'https://raw.githubusercontent.com/FifzzSENZE/Master-Proxy/master/proxies/socks4.txt',
            'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt'
        ],
        'socks5': [
            'https://raw.githubusercontent.com/mzyui/proxy-list/refs/heads/main/socks5.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
            'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5.txt',
            'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
            'https://vakhov.github.io/fresh-proxy-list/socks5.txt',
            'https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks5.txt',
            'https://raw.githubusercontent.com/FifzzSENZE/Master-Proxy/master/proxies/socks5.txt',
            'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
            'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt',
            'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt',
            'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt'
        ]
    }

class SourceHealthMonitor:
    def __init__(self):
        self.health_file = os.path.join(get_current_directory(), "source_health.json")
        self.health_data = self.load_health_data()

    def load_health_data(self):
        try:
            if os.path.exists(self.health_file):
                with open(self.health_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_health_data(self):
        try:
            with open(self.health_file, 'w', encoding='utf-8') as f:
                json.dump(self.health_data, f, indent=2)
        except:
            pass

    def update_source_health(self, url, success, response_time=0, proxy_count=0):
        if url not in self.health_data:
            self.health_data[url] = {
                "success_count": 0,
                "fail_count": 0,
                "total_requests": 0,
                "avg_response_time": 0,
                "last_success": None,
                "last_fail": None,
                "total_proxies": 0,
                "health_score": 100
            }

        data = self.health_data[url]
        data["total_requests"] += 1

        if success:
            data["success_count"] += 1
            data["last_success"] = time.time()
            data["total_proxies"] += proxy_count
            if data["avg_response_time"] == 0:
                data["avg_response_time"] = response_time
            else:
                data["avg_response_time"] = (data["avg_response_time"] + response_time) / 2
        else:
            data["fail_count"] += 1
            data["last_fail"] = time.time()
        success_rate = data["success_count"] / data["total_requests"]
        time_penalty = 0
        if data["last_fail"] and data["last_success"]:
            hours_since_last_success = (time.time() - data["last_success"]) / 3600
            if hours_since_last_success > 24:
                time_penalty = min(50, hours_since_last_success - 24)

        data["health_score"] = max(0, int((success_rate * 100) - time_penalty))

        self.save_health_data()

    def is_source_healthy(self, url, min_health_score=30):
        if url not in self.health_data:
            return True

        data = self.health_data[url]
        return data["health_score"] >= min_health_score

    def filter_healthy_sources(self, urls, min_health_score=30):
        return [url for url in urls if self.is_source_healthy(url, min_health_score)]
source_health_monitor = SourceHealthMonitor()

def get_proxy_urls():
    urls = get_proxy_urls_with_rotation()
    filtered_urls = {}
    
    for category, url_list in urls.items():
        unique_urls = list(dict.fromkeys(url_list))
        healthy_urls = source_health_monitor.filter_healthy_sources(unique_urls)
        if healthy_urls:
            filtered_urls[category] = healthy_urls
            
    return filtered_urls

async def fetch_api_proxies_async(session, api_type):
    try:
        if api_type == 'API_PROXYSCRAPE':
            url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=json"
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    proxies = []
                    if 'proxies' in data:
                        for proxy_info in data['proxies']:
                            if 'proxy' in proxy_info:
                                proxies.append(proxy_info['proxy'])
                    return proxies
                else:
                    return []
        elif api_type == 'API_GEONODE':
            url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    proxies = []
                    if 'data' in data:
                        for proxy_info in data['data']:
                            if 'ip' in proxy_info and 'port' in proxy_info:
                                proxy = f"{proxy_info['ip']}:{proxy_info['port']}"
                                proxies.append(proxy)
                    return proxies
                else:
                    return []
        elif api_type == 'API_PROXYLIST':
            url = "https://www.proxy-list.download/api/v1/get?type=http"
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    text = await response.text()
                    return [line.strip() for line in text.split('\n') if line.strip() and ':' in line]
                return []
        elif api_type == 'API_FREEPROXY':
            url = "https://free-proxy-list.net/"
            return []
        elif api_type == 'API_PROXYNOVA':
            url = "https://www.proxynova.com/proxy-server-list/"
            return []
        elif api_type == 'API_SPYSONE':
            url = "http://spys.one/en/free-proxy-list/"
            return []
        elif api_type == 'API_PROXYSCAN':
            url = "https://www.proxyscan.io/download?type=http"
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    text = await response.text()
                    return [line.strip() for line in text.split('\n') if line.strip() and ':' in line]
                return []
        elif api_type == 'API_PROXYROTATOR':
            url = "https://api.proxyrotator.com/free-proxy-list"
            return []
        elif api_type == 'API_PROXYHUB':
            url = "https://proxyhub.me/api/v1/proxies"
            return []
        elif api_type == 'API_PROXYSPACE':
            url = "https://proxyspace.pro/api/proxy"
            return []
    except Exception:
        return []

async def check_for_updates_async():
    urls = get_proxy_urls()
    session_data = load_session_data()
    
    async with aiohttp.ClientSession() as session:
        for proxy_type, url_list in urls.items():
            tasks = []
            for i, url in enumerate(url_list):
                tasks.append(get_file_hash_async(url, session))
            
            hashes = await asyncio.gather(*tasks)
            
            for i, url in enumerate(url_list):
                current_hash = hashes[i]
                old_hash = session_data.get(f'{proxy_type}_{i}_hash', '')
                
                if current_hash and current_hash != old_hash:
                    session_data[f'{proxy_type}_{i}_hash'] = current_hash
                    session_data[f'{proxy_type}_{i}_downloaded'] = []
    
    save_session_data(session_data)
    return session_data

async def get_proxy_count_async(proxy_type='all'):
    urls = get_proxy_urls()
    total_count = 0

    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls[proxy_type]:
                if url.startswith('API_'):
                    tasks.append(fetch_api_proxies_async(session, url))
                else:
                    tasks.append(session.get(url, timeout=30))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for i, response in enumerate(responses):
                url = urls[proxy_type][i]
                if url.startswith('API_'):
                    if isinstance(response, list):
                        total_count += len(response)
                else:
                    if not isinstance(response, Exception) and response.status == 200:
                        text = await response.text()
                        proxies = [line.strip() for line in text.split('\n') if line.strip()]
                        total_count += len(proxies)
    except:
        return 0

    return total_count

async def count_available_new_proxies_async(proxy_types):
    urls = get_proxy_urls()
    session_data = load_session_data()
    total_new_proxies = 0
    
    try:
        semaphore = asyncio.Semaphore(100)

        async def count_new_proxies(session, proxy_type, url_index, url):
            async with semaphore:
                try:
                    if url.startswith('API_'):
                        proxies_list = await fetch_api_proxies_async(session, url)
                    else:
                        async with session.get(url, timeout=30) as response:
                            if response.status == 200:
                                proxies_list = [line.strip() for line in (await response.text()).split('\n') if line.strip()]
                            else:
                                return 0

                    downloaded_hashes = set(session_data.get(f'{proxy_type}_{url_index}_downloaded', []))

                    new_count = 0
                    for proxy in proxies_list:
                        proxy_hash = hashlib.md5(proxy.encode()).hexdigest()
                        if proxy_hash not in downloaded_hashes:
                            new_count += 1

                    return new_count
                except Exception:
                    return 0

        async with aiohttp.ClientSession() as session:
            count_tasks = []
            for proxy_type in proxy_types:
                for url_index, url in enumerate(urls[proxy_type]):
                    count_tasks.append(count_new_proxies(session, proxy_type, url_index, url))
            
            counts = await asyncio.gather(*count_tasks)
            total_new_proxies = sum(counts)
            
    except Exception:
        return 0
    
    return total_new_proxies

async def download_proxies_with_progress_async(proxy_types, count, classify_output=False, will_check=False):
    urls = get_proxy_urls()
    session_data = load_session_data()
    all_proxies = []
    
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=show_loading_animation, args=("Đang thu thập proxy từ internet", stop_event))
    loading_thread.start()
    
    try:
        semaphore = asyncio.Semaphore(100)

        async def fetch_proxies(session, proxy_type, url_index, url):
            async with semaphore:
                start_time = time.time()
                try:
                    if url.startswith('API_'):
                        proxies = await fetch_api_proxies_async(session, url)
                        response_time = time.time() - start_time
                        source_health_monitor.update_source_health(url, True, response_time, len(proxies))
                        return proxy_type, url_index, proxies
                    else:
                        async with session.get(url, timeout=30) as response:
                            response_time = time.time() - start_time
                            if response.status == 200:
                                proxies = [line.strip() for line in (await response.text()).split('\n') if line.strip()]
                                source_health_monitor.update_source_health(url, True, response_time, len(proxies))
                                return proxy_type, url_index, proxies
                            else:
                                source_health_monitor.update_source_health(url, False, response_time, 0)
                                return proxy_type, url_index, []
                except Exception:
                    response_time = time.time() - start_time
                    source_health_monitor.update_source_health(url, False, response_time, 0)
                    return proxy_type, url_index, []

        async with aiohttp.ClientSession() as session:
            download_tasks = []
            for proxy_type in proxy_types:
                for url_index, url in enumerate(urls[proxy_type]):
                    download_tasks.append(fetch_proxies(session, proxy_type, url_index, url))
            
            results = await asyncio.gather(*download_tasks)
            
            for proxy_type, url_index, proxies_list in results:
                downloaded_hashes = set(session_data.get(f'{proxy_type}_{url_index}_downloaded', []))
                
                new_proxies = []
                for proxy in proxies_list:
                    proxy_hash = hashlib.md5(proxy.encode()).hexdigest()
                    if proxy_hash not in downloaded_hashes:
                        new_proxies.append(proxy)
                        downloaded_hashes.add(proxy_hash)
                
                all_proxies.extend(new_proxies)
                session_data[f'{proxy_type}_{url_index}_downloaded'] = list(downloaded_hashes)
    finally:
        stop_event.set()
        loading_thread.join()
    
    if len(all_proxies) == 0:
        reset_session_data()
        console.print(f"\n[yellow]Đã hết proxy mới có sẵn, cache đã được reset tự động.[/yellow]")
        return [], None

    if len(all_proxies) < count:
        count = len(all_proxies)
        console.print(f"[yellow]Chỉ có thể lấy {count} proxy[/yellow]")

    selected_proxies = random.sample(all_proxies, count) if len(all_proxies) >= count else all_proxies
    save_session_data(session_data)

    output_file = None

    if not will_check:
        if classify_output and len(proxy_types) > 1:
            classified_proxies = {}
            for ptype in proxy_types:
                classified_proxies[ptype] = []

            for i, proxy in enumerate(selected_proxies):
                proxy_type = proxy_types[i % len(proxy_types)]
                classified_proxies[proxy_type].append(proxy)

            for ptype, plist in classified_proxies.items():
                if plist:
                    output_file = os.path.join(get_current_directory(), f"proxy_{ptype}.txt")
                    with open(output_file, 'a', encoding='utf-8') as f:
                        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                            f.write("\n")
                        f.write('\n'.join(plist))
                    console.print(f"[green]✓ Đã lưu {len(plist)} proxy {ptype}: {output_file}[/green]")
        else:
            if len(proxy_types) == 1 and proxy_types[0] != 'all':
                output_file = os.path.join(get_current_directory(), f"proxy_{proxy_types[0]}.txt")
            else:
                output_file = os.path.join(get_current_directory(), "proxy_public.txt")

            with open(output_file, 'a', encoding='utf-8') as f:
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    f.write("\n")
                f.write('\n'.join(selected_proxies))
            console.print(f"[green]✓ Đã lưu {len(selected_proxies)} proxy: {output_file}[/green]")

    return selected_proxies, output_file

async def handle_system_config(proxy_manager):
    while True:
        clear_screen()
        show_header()
        
        console.print("\n[cyan]Cấu hình hệ thống:[/cyan]")
        console.print("\n1. Cài đặt kiểm tra proxy")
        console.print("2. Quản lý proxy yêu thích")
        console.print("3. Quản lý danh sách chặn")
        console.print("4. Xuất/Nhập cấu hình")
        console.print("5. Dọn dẹp dữ liệu cũ")
        console.print("6. Quay lại")
        
        try:
            choice = int(console.input("\n[bold bright_cyan]Lựa chọn của bạn (1-6): [/bold bright_cyan]"))
            
            if choice == 1:
                await configure_proxy_settings(proxy_manager)
            elif choice == 2:
                await manage_favorites(proxy_manager)
            elif choice == 3:
                await manage_blacklist(proxy_manager)
            elif choice == 4:
                await handle_config_file(proxy_manager)
            elif choice == 5:
                await cleanup_data(proxy_manager)
            elif choice == 6:
                break
            else:
                console.print("[red]Lựa chọn không hợp lệ![/red]")
        except ValueError:
            console.print("[red]Vui lòng nhập số từ 1-6![/red]")
        
async def configure_proxy_settings(proxy_manager):
    clear_screen()
    show_header()
    
    console.print("\n[cyan]Cài đặt kiểm tra proxy:[/cyan]")
    
    try:
        timeout = int(console.input("\n[white]Thời gian chờ tối đa (giây, hiện tại: {}): [/white]".format(
            proxy_manager.config['timeout']
        )))
        if timeout > 0:
            proxy_manager.config['timeout'] = timeout
    except ValueError:
        pass

    try:
        threads = int(console.input("\n[white]Số luồng tối đa (hiện tại: {}): [/white]".format(
            proxy_manager.config['max_threads']
        )))
        if threads > 0:
            proxy_manager.config['max_threads'] = threads
    except ValueError:
        pass
    
    if get_yes_no_input("\n[cyan]Bạn có muốn thêm URL test mới không? (y/n): [/cyan]"):
        url = console.input("\n[white]Nhập URL (bao gồm http:// hoặc https://): [/white]")
        try:
            async with httpx.AsyncClient() as client:
                await client.head(url, timeout=5)
            proxy_manager.config['test_urls'].append({
                'url': url,
                'weight': 1,
                'timeout': proxy_manager.config['timeout'],
                'ssl': url.startswith('https')
            })
        except:
            console.print("[red]Không thể kết nối đến URL này![/red]")
    
    save_config(proxy_manager.config)
    console.print("\n[green]Đã lưu cấu hình![/green]")
    await asyncio.sleep(1)

async def manage_favorites(proxy_manager):
    while True:
        clear_screen()
        show_header()
        
        favorites = proxy_manager.get_favorites()
        console.print("\n[cyan]Proxy yêu thích:[/cyan]")
        
        if not favorites:
            console.print("[yellow]Không có proxy yêu thích nào![/yellow]")
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("STT", style="cyan", justify="right")
            table.add_column("Proxy", style="green")
            table.add_column("Lần kiểm tra cuối", style="yellow")
            table.add_column("Trạng thái", style="blue")
            
            for i, proxy in enumerate(favorites, 1):
                info = proxy_manager.get_proxy_info(proxy)
                last_check = "Chưa kiểm tra"
                status = "Không rõ"
                
                if info.get('last_check'):
                    last_check = datetime.fromisoformat(info['last_check']).strftime('%Y-%m-%d %H:%M')
                    if info['checks']:
                        status = info['checks'][-1]['result']['status']
                
                table.add_row(str(i), proxy, last_check, status)
            
            console.print(table)
        
        console.print("\n1. Thêm proxy yêu thích")
        console.print("2. Xóa proxy yêu thích")
        console.print("3. Kiểm tra lại tất cả")
        console.print("4. Quay lại")
        
        try:
            choice = int(console.input("\n[bold bright_cyan]Lựa chọn của bạn (1-4): [/bold bright_cyan]"))
            
            if choice == 1:
                proxy = console.input("\n[white]Nhập proxy (IP:PORT): [/white]")
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$', proxy):
                    proxy_manager.add_to_favorites(proxy)
                    console.print("[green]Đã thêm vào danh sách yêu thích![/green]")
                else:
                    console.print("[red]Định dạng proxy không hợp lệ![/red]")
            
            elif choice == 2:
                if favorites:
                    try:
                        idx = int(console.input("\n[white]Nhập STT proxy cần xóa: [/white]")) - 1
                        if 0 <= idx < len(favorites):
                            proxy_manager.remove_from_favorites(favorites[idx])
                            console.print("[green]Đã xóa khỏi danh sách yêu thích![/green]")
                        else:
                            console.print("[red]STT không hợp lệ![/red]")
                    except ValueError:
                        console.print("[red]Vui lòng nhập số![/red]")
            
            elif choice == 3:
                if favorites:
                    checker = ProxyChecker(proxy_manager)
                    await checker.check_proxies(favorites)
                    console.print("[green]Đã kiểm tra xong![/green]")
                await asyncio.sleep(1)
            
            elif choice == 4:
                break
            
        except ValueError:
            console.print("[red]Vui lòng nhập số từ 1-4![/red]")
        
        await asyncio.sleep(0.5)

async def manage_blacklist(proxy_manager):
    while True:
        clear_screen()
        show_header()
        
        console.print("\n[cyan]Danh sách chặn:[/cyan]")
        blacklist = list(proxy_manager.config['blacklisted_ips'])
        
        if not blacklist:
            console.print("[yellow]Danh sách chặn trống![/yellow]")
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("STT", style="cyan", justify="right")
            table.add_column("IP", style="red")
            
            for i, ip in enumerate(blacklist, 1):
                table.add_row(str(i), ip)
            
            console.print(table)
        
        console.print("\n1. Thêm IP vào danh sách chặn")
        console.print("2. Xóa IP khỏi danh sách chặn")
        console.print("3. Xóa toàn bộ danh sách")
        console.print("4. Quay lại")
        
        try:
            choice = int(console.input("\n[bold bright_cyan]Lựa chọn của bạn (1-4): [/bold bright_cyan]"))
            
            if choice == 1:
                ip = console.input("\n[white]Nhập IP cần chặn: [/white]")
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                    proxy_manager.config['blacklisted_ips'].add(ip)
                    save_config(proxy_manager.config)
                    console.print("[green]Đã thêm vào danh sách chặn![/green]")
                else:
                    console.print("[red]Định dạng IP không hợp lệ![/red]")
            
            elif choice == 2:
                if blacklist:
                    try:
                        idx = int(console.input("\n[white]Nhập STT IP cần xóa: [/white]")) - 1
                        if 0 <= idx < len(blacklist):
                            proxy_manager.config['blacklisted_ips'].remove(blacklist[idx])
                            save_config(proxy_manager.config)
                            console.print("[green]Đã xóa khỏi danh sách chặn![/green]")
                        else:
                            console.print("[red]STT không hợp lệ![/red]")
                    except ValueError:
                        console.print("[red]Vui lòng nhập số![/red]")
            
            elif choice == 3:
                if get_yes_no_input("\n[red]Bạn có chắc muốn xóa toàn bộ danh sách chặn? (y/n): [/red]"):
                    proxy_manager.config['blacklisted_ips'].clear()
                    save_config(proxy_manager.config)
                    console.print("[green]Đã xóa toàn bộ danh sách chặn![/green]")
            
            elif choice == 4:
                break
            
        except ValueError:
            console.print("[red]Vui lòng nhập số từ 1-4![/red]")
        
        await asyncio.sleep(0.5)

async def handle_config_file(proxy_manager):
    clear_screen()
    show_header()
    
    console.print("\n[cyan]Xuất/Nhập cấu hình:[/cyan]")
    console.print("\n1. Xuất cấu hình")
    console.print("2. Nhập cấu hình")
    console.print("3. Quay lại")
    
    try:
        choice = int(console.input("\n[bold bright_cyan]Lựa chọn của bạn (1-3): [/bold bright_cyan]"))
        
        if choice == 1:
            export_path = os.path.join(get_current_directory(), 'proxy_config_export.json')
            with open(export_path, 'w') as f:
                json.dump({
                    'config': proxy_manager.config,
                    'database': proxy_manager.proxies_db
                }, f, indent=4)
            console.print(f"\n[green]Đã xuất cấu hình tại: {export_path}[/green]")
        
        elif choice == 2:
            try:
                import_path = os.path.join(get_current_directory(), 'proxy_config_export.json')
                if os.path.exists(import_path):
                    with open(import_path, 'r') as f:
                        data = json.load(f)
                        proxy_manager.config.update(data.get('config', {}))
                        proxy_manager.proxies_db.update(data.get('database', {}))
                    save_config(proxy_manager.config)
                    proxy_manager.save_database()
                    console.print("\n[green]Đã nhập cấu hình thành công![/green]")
                else:
                    console.print("\n[red]Không tìm thấy file cấu hình![/red]")
            except Exception as e:
                console.print(f"\n[red]Lỗi khi nhập cấu hình: {str(e)}[/red]")
        
    except ValueError:
        console.print("[red]Vui lòng nhập số từ 1-3![/red]")
    
    await asyncio.sleep(1)

async def cleanup_data(proxy_manager):
    clear_screen()
    show_header()
    
    console.print("\n[cyan]Dọn dẹp dữ liệu:[/cyan]")
    
    try:
        days = int(console.input("\n[white]Xóa dữ liệu cũ hơn bao nhiêu ngày (mặc định 30): [/white]") or "30")
        if days > 0:
            proxy_manager.cleanup_old_records(days)
            console.print("\n[green]Đã dọn dẹp dữ liệu thành công![/green]")
        else:
            console.print("[red]Số ngày phải lớn hơn 0![/red]")
    except ValueError:
        console.print("[red]Vui lòng nhập số![/red]")
    
    await asyncio.sleep(1)

async def get_free_proxies_async():
    clear_screen()
    show_header()
    console.print(f"\n[cyan]Đang kiểm tra cập nhật proxy từ nhiều kho lưu trữ ...[/cyan]")

    await check_for_updates_async()

    console.print(f"\n[cyan]Chức năng lấy proxy public miễn phí[/cyan]")

    last_updated = await get_latest_commit_from_all_repos_async()
    console.print(f"[yellow]Cập nhật lần cuối: {last_updated}[/yellow]")

    total_count = await get_proxy_count_async('all')
    if total_count == 0:
        console.print(f"\n[red]✗ Không thể kết nối tới các kho lưu trữ proxy hoặc không có proxy nào![/red]")
        console.input(f"\n[cyan]Nhấn Enter để quay lại menu chính...[/cyan]")
        return

    console.print(f"[green]Tổng số proxy hiện có sẵn: {total_count:,}[/green]")

    while True:
        try:
            count = int(console.input(f"\n[cyan]Nhập số lượng proxy muốn lấy (1-{total_count:,}):[/cyan] [white]"))
            if 1 <= count <= total_count:
                break
            console.print(f"[red]Vui lòng nhập số từ 1 đến {total_count:,}![/red]")
        except ValueError:
            console.print(f"[red]Vui lòng nhập số hợp lệ![/red]")

    choose_type = get_yes_no_input(f"\n[cyan]Bạn muốn chọn proxy theo loại không? (y/n):[/cyan]")

    if choose_type:
        console.print(f"\n[cyan]Chọn loại proxy (có thể chọn nhiều, cách nhau bởi dấu phẩy):[/cyan]")
        console.print(f"[white]1. HTTP[/white]")
        console.print(f"[white]2. HTTPS[/white]")
        console.print(f"[white]3. SOCKS4[/white]")
        console.print(f"[white]4. SOCKS5[/white]")

        while True:
            choices = console.input(f"\n[cyan]Nhập lựa chọn (ví dụ: 1,2 hoặc 3,4):[/cyan] [white]").strip()
            try:
                choice_list = [int(x.strip()) for x in choices.split(',')]
                if all(1 <= x <= 4 for x in choice_list):
                    proxy_types = []
                    for choice in choice_list:
                        if choice == 1:
                            proxy_types.append('http')
                        elif choice == 2:
                            proxy_types.append('https')
                        elif choice == 3:
                            proxy_types.append('socks4')
                        elif choice == 4:
                            proxy_types.append('socks5')
                    break
                console.print(f"[red]Vui lòng chỉ nhập số 1, 2, 3 hoặc 4![/red]")
            except ValueError:
                console.print(f"[red]Định dạng không hợp lệ! Ví dụ: 1,2[/red]")
    else:
        proxy_types = ['all']

    console.print(f"\n[yellow]Đang kiểm tra số proxy mới có sẵn...[/yellow]")
    available_new_proxies = await count_available_new_proxies_async(proxy_types)

    if available_new_proxies == 0:
        reset_session_data()
        console.print(f"\n[yellow]✓ Đã hết proxy mới có sẵn, cache đã được reset. Bạn có thể chạy lại để lấy tất cả proxy từ đầu.[/yellow]")
        console.input(f"\n[cyan]Nhấn Enter để quay lại menu chính...[/cyan]")
        return

    if available_new_proxies < count:
        console.print(f"\n[yellow]⚠ Chỉ còn {available_new_proxies:,} proxy mới chưa được lấy (bạn yêu cầu {count:,})[/yellow]")
        confirm = get_yes_no_input(f"[cyan]Bạn có muốn lấy {available_new_proxies:,} proxy này không? (y/n):[/cyan]")
        if not confirm:
            console.input(f"\n[cyan]Nhấn Enter để quay lại menu chính...[/cyan]")
            return
        count = available_new_proxies
    else:
        console.print(f"[green]✓ Còn {available_new_proxies:,} proxy mới có thể lấy.[/green]")

    classify_output = False
    if len(proxy_types) > 1:
        classify_output = get_yes_no_input(f"\n[cyan]Bạn muốn phân loại proxy ở file đầu ra không? (y/n):[/cyan]")

    check_now = get_yes_no_input(f"\n[cyan]Bạn muốn kiểm tra proxy sau khi tải không? (y/n):[/cyan]")

    check_settings = None
    if check_now:
        check_settings = {}

        output_file = console.input(f"\n[cyan]Nhập tên file để lưu kết quả check (để trống sẽ dùng 'proxy_live.txt'):[/cyan] [white]")
        if not output_file.strip():
            check_settings['output_file'] = 'proxy_live.txt'
        else:
            if not output_file.endswith('.txt'):
                output_file += '.txt'
            check_settings['output_file'] = output_file

        classify_proxies = get_yes_no_input(f"\n[cyan]Bạn muốn phân loại proxy khi check không? (y/n):[/cyan]")
        check_settings['classify'] = classify_proxies

        if check_settings['classify']:
            check_settings['classify_option'] = console.input(f"\n[cyan]Phân loại theo (1) Quốc gia, (2) Loại proxy, (3) Cả hai? Nhập số:[/cyan] [white]")

        while True:
            try:
                max_threads = int(console.input(f"[cyan]Nhập số luồng (tối thiểu 1):[/cyan] [white]"))
                if max_threads >= 1:
                    check_settings['max_threads'] = max_threads
                    break
                console.print(f"[red]Số luồng phải lớn hơn hoặc bằng 1![/red]")
            except ValueError:
                console.print(f"[red]Vui lòng nhập số hợp lệ![/red]")

    clear_screen()
    show_header()
    console.print(f"\n[yellow]Bắt đầu thu thập proxy từ internet...[/yellow]")

    try:
        proxies, output_file = await download_proxies_with_progress_async(proxy_types, count, classify_output, check_now)

        if not proxies:
            console.input(f"\n[cyan]Nhấn Enter để quay lại menu chính...[/cyan]")
            return

        console.print(f"\n[green]✓ Đã thu thập thành công {len(proxies):,} proxy![/green]")

        if check_now:
            console.print(f"\n[yellow]Bắt đầu kiểm tra proxy...[/yellow]")
            time.sleep(1)

            if classify_output:
                console.print(f"\n[yellow]Chuyển sang kiểm tra proxy. Vui lòng chọn file bạn muốn kiểm tra...[/yellow]")
                time.sleep(2)
                clear_screen()
                show_header()
                console.print(f"\n[cyan]Vui lòng chọn file cần kiểm tra...[/cyan]")
                proxy_file = select_proxy_file()
                if proxy_file and validate_proxy_file(proxy_file):
                    run_proxy_check(proxy_file, check_settings)
            else:
                run_proxy_check_from_memory(proxies, check_settings)

    except Exception as e:
        console.print(f"\n[red]Lỗi khi tải proxy: {str(e)}[/red]")

    console.input(f"\n[cyan]Nhấn Enter để quay lại menu chính...[/cyan]")

async def handle_proxy_check(proxy_manager, source_type='file', proxy_file=None, proxy_list=None):
    settings = {
        'level': 'normal',
        'output_file': 'working_proxies.txt'
    }

    clear_screen()
    show_header()

    console.print("\n[cyan]Chọn mức độ kiểm tra:[/cyan]")
    console.print("[white]1. Nhanh (2 test, yêu cầu tốc độ thấp)[/white]")
    console.print("[white]2. Thường (3 test, yêu cầu tốc độ trung bình)[/white]")
    console.print("[white]3. Kỹ lưỡng (5 test, yêu cầu tốc độ cao)[/white]")
    
    while True:
        try:
            choice = int(console.input("\n[bold bright_cyan]Lựa chọn của bạn (1-3): [/bold bright_cyan]"))
            if 1 <= choice <= 3:
                settings['level'] = ['fast', 'normal', 'thorough'][choice - 1]
                break
        except ValueError:
            pass
        console.print("[red]Vui lòng chọn 1, 2 hoặc 3![/red]")

    checker = ProxyChecker(proxy_manager)
    
    if source_type == 'file':
        with open(proxy_file, 'r') as f:
            proxy_list = [line.strip() for line in f if line.strip()]
    
    console.print(f"\n[yellow]Bắt đầu kiểm tra {len(proxy_list)} proxy...[/yellow]")
    
    results = await checker.check_proxies(proxy_list, settings['level'])
    
    working_proxies = [r for r in results if r['status'] == 'working']
    slow_proxies = [r for r in results if r['status'] == 'slow']
    failed_proxies = [r for r in results if r['status'] == 'failed']

    clear_screen()
    show_header()
    
    console.print("\n[green]✓ KIỂM TRA HOÀN TẤT![/green]")
    console.print(f"[cyan]Tổng số proxy:[/cyan] [white]{len(proxy_list):,}[/white]")
    console.print(f"[cyan]Proxy hoạt động tốt:[/cyan] [green]{len(working_proxies):,}[/green]")
    console.print(f"[cyan]Proxy chậm:[/cyan] [yellow]{len(slow_proxies):,}[/yellow]")
    console.print(f"[cyan]Proxy không hoạt động:[/cyan] [red]{len(failed_proxies):,}[/red]")

    if working_proxies:
        save_path = os.path.join(get_current_directory(), settings['output_file'])
        with open(save_path, 'w') as f:
            for proxy in working_proxies:
                f.write(f"{proxy['url']}\n")
        console.print(f"\n[green]Đã lưu proxy hoạt động vào:[/green] [white]{save_path}[/white]")
        
        if get_yes_no_input("\n[cyan]Bạn có muốn xem chi tiết về các proxy hoạt động không? (y/n): [/cyan]"):
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Proxy", style="cyan")
            table.add_column("Tốc độ (Mbps)", justify="right", style="green")
            table.add_column("Độ trễ (ms)", justify="right", style="yellow")
            table.add_column("Giao thức", style="blue")
            
            for proxy in working_proxies:
                table.add_row(
                    proxy['url'],
                    f"{proxy['speed']:.2f}",
                    f"{proxy['latency']:.0f}",
                    ", ".join(proxy['protocols'])
                )
            console.print(table)

    console.input(f"\n[cyan]Nhấn Enter để quay lại menu chính...[/cyan]")

async def handle_proxy_collection(proxy_manager):
    clear_screen()
    show_header()
    
    console.print("\n[cyan]Thu thập proxy từ nhiều nguồn...[/cyan]")
    
    collector = ProxyCollector()
    proxies = await collector.collect_all()
    
    if not proxies:
        console.print("\n[red]Không tìm thấy proxy nào![/red]")
        console.input("\n[cyan]Nhấn Enter để quay lại menu chính...[/cyan]")
        return
    
    console.print(f"\n[green]Đã thu thập được {len(proxies)} proxy![/green]")
    
    if get_yes_no_input("\n[cyan]Bạn có muốn kiểm tra các proxy vừa thu thập không? (y/n): [/cyan]"):
        await handle_proxy_check(proxy_manager, source_type='memory', proxy_list=proxies)
    else:
        save_path = os.path.join(get_current_directory(), 'collected_proxies.txt')
        with open(save_path, 'w') as f:
            for proxy in proxies:
                f.write(f"{proxy}\n")
        console.print(f"\n[green]Đã lưu danh sách proxy vào:[/green] [white]{save_path}[/white]")
        console.input("\n[cyan]Nhấn Enter để quay lại menu chính...[/cyan]")

def run_proxy_check(proxy_file, settings):
    console.print(f"\n[yellow]Đang kiểm tra proxy với {settings['max_threads']} luồng...\n[/yellow]")

    with open(proxy_file, 'r', encoding='utf-8') as f:
        proxies = [line.strip() for line in f if line.strip()]

    output_path = os.path.join(get_current_directory(), settings['output_file'])

    results = check_proxies(
        proxies,
        settings['classify'],
        settings.get('classify_option', 'n'),
        output_path,
        settings['max_threads']
    )
    live_count = len(results)

    if live_count > 0:
        console.print(f"\n[green]✓ KIỂM TRA HOÀN TẤT![/green]")
        console.print(f"[cyan]Tổng proxy:[/cyan] [white]{len(proxies):,}[/white]")
        console.print(f"[cyan]Proxy sống:[/cyan] [white]{live_count:,}[/white]")
        console.print(f"[cyan]Proxy chết:[/cyan] [white]{len(proxies) - live_count:,}[/white]")
        console.print(f"[cyan]Kết quả lưu tại:[/cyan] [white]{output_path}[/white]")
    else:
        console.print(f"\n[red]✓ KIỂM TRA HOÀN TẤT![/red]")
        console.print(f"[cyan]Tổng proxy:[/cyan] [white]{len(proxies):,}[/white]")
        console.print(f"[cyan]Proxy sống:[/cyan] [white]{live_count:,}[/white]")
        console.print(f"[cyan]Proxy chết:[/cyan] [white]{len(proxies) - live_count:,}[/white]")

def run_proxy_check_from_memory(proxy_list, settings):
    console.print(f"\n[yellow]Đang kiểm tra proxy với {settings['max_threads']} luồng...\n[/yellow]")

    output_path = os.path.join(get_current_directory(), settings['output_file'])

    results = check_proxies(
        proxy_list,
        settings['classify'],
        settings.get('classify_option', 'n'),
        output_path,
        settings['max_threads']
    )
    live_count = len(results)

    if live_count > 0:
        console.print(f"\n[green]✓ KIỂM TRA HOÀN TẤT![/green]")
        console.print(f"[cyan]Tổng proxy:[/cyan] [white]{len(proxy_list):,}[/white]")
        console.print(f"[cyan]Proxy sống:[/cyan] [white]{live_count:,}[/white]")
        console.print(f"[cyan]Proxy chết:[/cyan] [white]{len(proxy_list) - live_count:,}[/white]")
        console.print(f"[cyan]Kết quả lưu tại:[/cyan] [white]{output_path}[/white]")
    else:
        console.print(f"\n[red]✓ KIỂM TRA HOÀN TẤT![/red]")
        console.print(f"[cyan]Tổng proxy:[/cyan] [white]{len(proxy_list):,}[/white]")
        console.print(f"[cyan]Proxy sống:[/cyan] [white]{live_count:,}[/white]")
        console.print(f"[cyan]Proxy chết:[/cyan] [white]{len(proxy_list) - live_count:,}[/white]")

def proceed_with_check_rich(source_type, proxy_file=None, proxy_list=None, user_settings=None):
    config_title = create_rainbow_text("◆ CẤU HÌNH XÁC THỰC ◆")
    console.print("\n" + config_title)

    output_file = console.input("[bold bright_cyan]◆ Output filename (default: 'proxy_live.txt'): [/bold bright_cyan]").strip()
    if not output_file:
        output_file = 'proxy_live.txt'
    elif not output_file.endswith('.txt'):
        output_file += '.txt'

    classify_proxies = console.input("[bold bright_cyan]◆ Enable proxy classification? (y/n): [/bold bright_cyan]").strip().lower() == 'y'
    classify_option = 'n'

    if classify_proxies:
        console.print("\n[bold bright_yellow]◆ Classification Options ◆[/bold bright_yellow]")
        console.print("[bold red on black]【 1 】[/bold red on black] [bright_green]Phân loại theo địa lý[/bright_green]")
        console.print("[bold orange1 on black]【 2 】[/bold orange1 on black] [bright_blue]Phân loại theo giao thức[/bright_blue]")
        console.print("[bold yellow on black]【 3 】[/bold yellow on black] [bright_magenta]Phân loại toàn diện[/bright_magenta]")
        classify_option = console.input("[bold bright_cyan]◆ Chọn tùy chọn (1/2/3): [/bold bright_cyan]").strip()

    if user_settings:
        max_threads = user_settings['max_threads']
        console.print(f"[green]✅ Sử dụng {max_threads} luồng từ cấu hình[/green]")
    else:
        max_threads = 100
        if console.input(f"[bold bright_cyan]◆ Sử dụng số luồng mặc định ({max_threads})? (y/n): [/bold bright_cyan]").strip().lower() == 'n':
            while True:
                try:
                    max_threads = int(console.input("[bold bright_cyan]◆ Nhập số luồng (tối thiểu 1): [/bold bright_cyan]"))
                    if max_threads >= 1:
                        break
                    console.print("[bold bright_red]◆ Số luồng phải lớn hơn 0 ◆[/bold bright_red]")
                except ValueError:
                    console.print("[bold bright_red]◆ Giá trị số luồng không hợp lệ ◆[/bold bright_red]")

    clear_screen()
    show_header_rich()

    settings = {
        'output_file': output_file,
        'classify': classify_proxies,
        'classify_option': classify_option,
        'max_threads': max_threads,
        'use_rich': True
    }

    if source_type == 'file':
        run_proxy_check(proxy_file, settings)
    else:
        run_proxy_check_from_memory(proxy_list, settings)

def proceed_with_check(source_type, proxy_file=None, proxy_list=None):
    output_file = console.input(f"\n[cyan]Nhập tên file để lưu kết quả (để trống sẽ dùng 'proxy_live.txt'):[/cyan] [white]")
    if not output_file.strip():
        output_file = 'proxy_live.txt'
    else:
        if not output_file.endswith('.txt'):
            output_file += '.txt'

    classify_proxies = get_yes_no_input(f"\n[cyan]Bạn muốn phân loại proxy không? (y/n):[/cyan]")
    classify_option = None
    if classify_proxies:
        classify_option = console.input(f"\n[cyan]Bạn muốn phân loại theo (1) Quốc gia, (2) Loại proxy, (3) Cả hai? Nhập số tương ứng:[/cyan] [white]")
    else:
        classify_option = 'n'

    while True:
        try:
            max_threads = int(console.input(f"[cyan]Nhập số luồng (tối thiểu 1):[/cyan] [white]"))
            if max_threads >= 1:
                break
            console.print(f"[red]Số luồng phải lớn hơn hoặc bằng 1![/red]")
        except ValueError:
            console.print(f"[red]Vui lòng nhập số hợp lệ![/red]")

    clear_screen()
    show_header()

    settings = {
        'output_file': output_file,
        'classify': classify_proxies,
        'classify_option': classify_option,
        'max_threads': max_threads
    }

    if source_type == 'file':
        run_proxy_check(proxy_file, settings)
    else:
        run_proxy_check_from_memory(proxy_list, settings)



async def main():
    proxy_manager = ProxyManager()

    clear_screen()
    show_header()
    show_rainbow_message("◆ Đang khởi động Proxy Master Suite ◆".center(60), duration=1)

    await asyncio.sleep(1)

    while True:
        clear_screen()
        show_header()

        config = load_config()
        
        if config.get('use_rich_interface', True):
            welcome_text = create_rainbow_text("◆◆◆ CHÀO MỪNG ĐẾN VỚI PROXY MASTER SUITE ◆◆◆")

            rainbow_line = create_rainbow_text("─" * 140)

            menu_items = [
                [Text("【 1 】", style="bold red on black"), "🔍", Text("Kiểm tra và phân tích proxy", style="bold bright_green")],
                [Text("【 2 】", style="bold orange1 on black"), "📥", Text("Thu thập proxy miễn phí", style="bold bright_blue")],
                [Text("【 3 】", style="bold yellow on black"), "⚙️", Text("Cấu hình hệ thống", style="bold bright_magenta")],
                [Text("【 4 】", style="bold cyan on black"), "🚪", Text("Thoát chương trình", style="bold bright_red")]
            ]

            menu_text = []
            for number, icon, desc in menu_items:
                menu_text.append(
                    Text.assemble(
                        (number, "bold"),
                        Text("  "),
                        (icon, "bold"),
                        Text("  "),
                        desc
                    )
                )

            menu_content = Align.center(
                Text.assemble(
                    (rainbow_line, "bold"),
                    Text("\n\n"),
                    (welcome_text, "bold"),
                    Text("\n\n"),
                    Text("Chọn chức năng:", style="italic bright_white"),
                    Text("\n\n"),
                    *(text for text in menu_text),
                    Text("\n"),
                    (rainbow_line, "bold")
                )
            )

            menu_panel = Panel(
                menu_content,
                border_style="bright_magenta",
                padding=(0, 3),
                title=create_rainbow_text("◆◆◆ MENU CHÍNH ◆◆◆"),
                title_align="center",
                width=150,
                box=ROUNDED
            )
            console.print(menu_panel, justify="center")
            choice = console.input("\n[bold bright_cyan]◆ Nhập lựa chọn của bạn (1-4): [/bold bright_cyan]").strip()
        else:
            show_header()
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}Chào mừng bạn đến với tool về proxy!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Vui lòng chọn chức năng bạn muốn sử dụng:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}1. Kiểm tra Proxy từ file có sẵn")
            print(f"{Fore.WHITE}2. Lấy Proxy Public Free")
            print(f"{Fore.WHITE}3. ⚙️  Cấu hình Tool")
            print(f"{Fore.WHITE}4. Thoát{Style.RESET_ALL}")
            choice = input(f"\n{Fore.CYAN}Nhập lựa chọn của bạn (1-4):{Style.RESET_ALL} {Fore.WHITE}").strip()

        if choice == '1':
            if config.get('use_rich_interface', True):
                show_rainbow_message("◆ Đang khởi động module kiểm tra proxy ◆".center(60), duration=2)
                time.sleep(0.5)
                clear_screen()
                show_header_rich()

                use_config, current_config = ask_use_config()
                user_settings = get_user_settings(use_config, current_config)

                input_title = create_rainbow_text("◆◆◆ LỰA CHỌN PHƯƠNG THỨC NHẬP PROXY ◆◆◆")

                input_panel = Panel(
                    input_title + "\n\n" +
                    Text("「 Chọn phương thức nhập proxy 」", style="italic bright_white") + "\n\n" +
                    Text("【 1 】", style="bold red on black") + Text(" Chọn file từ hệ thống", style="bold bright_green") + "\n" +
                    Text("【 2 】", style="bold orange1 on black") + Text(" Nhập thủ công", style="bold bright_blue") + "\n\n" +
                    Text("⚠️  Định dạng: ip:port, mỗi proxy một dòng", style="italic yellow"),
                    border_style=create_gradient_border(),
                    padding=(2, 4),
                    title="[bold bright_cyan]◆◆◆ BẢNG ĐIỀU KHIỂN NHẬP ◆◆◆[/bold bright_cyan]",
                    title_align="center"
                )
                console.print(input_panel, justify="center")
                input_choice = console.input("\n[bold bright_cyan]◆ Chọn phương thức (1 hoặc 2): [/bold bright_cyan]").strip()
            else:
                print(f"\n{Fore.YELLOW}{Style.BRIGHT}Đang khởi động công cụ kiểm tra proxy...{Style.RESET_ALL}")
                time.sleep(1.5)
                clear_screen()
                show_header()

                print(f"\n{Fore.CYAN}{Style.BRIGHT}Chọn cách nhập proxy:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}1. Chọn file từ máy tính")
                print(f"{Fore.WHITE}2. Nhập thủ công")
                print(f"{Fore.YELLOW}Ghi chú: Định dạng proxy phải là ip:port và mỗi proxy một hàng{Style.RESET_ALL}")
                input_choice = input(f"\n{Fore.CYAN}Nhập lựa chọn của bạn (1 hoặc 2):{Style.RESET_ALL} {Fore.WHITE}").strip()
            
            if choice == '1':
                clear_screen()
                show_header()
                console.print("\n[cyan]Chọn nguồn proxy:[/cyan]")
                console.print("1. Từ file")
                console.print("2. Nhập trực tiếp")
                
                try:
                    source_choice = int(console.input("\n[bold bright_cyan]Lựa chọn của bạn (1-2): [/bold bright_cyan]"))
                    
                    if source_choice == 1:
                        console.print("\n[cyan]Vui lòng chọn file proxy...[/cyan]")
                        proxy_file = filedialog.askopenfilename(
                            title="Chọn file proxy",
                            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                        )
                        
                        if proxy_file:
                            await handle_proxy_check(proxy_manager, 'file', proxy_file=proxy_file)
                        else:
                            console.print("\n[red]Không có file nào được chọn![/red]")
                    
                    elif source_choice == 2:
                        console.print("\n[cyan]Nhập proxy (một proxy mỗi dòng, nhấn Enter hai lần để kết thúc):[/cyan]")
                        proxies = []
                        while True:
                            line = console.input().strip()
                            if not line:
                                break
                            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$', line):
                                proxies.append(line)
                        
                        if proxies:
                            await handle_proxy_check(proxy_manager, 'memory', proxy_list=proxies)
                        else:
                            console.print("\n[red]Không có proxy nào được nhập![/red]")
                
                except ValueError:
                    console.print("[red]Lựa chọn không hợp lệ![/red]")
            
            elif choice == '2':
                await handle_proxy_collection(proxy_manager)
            
            elif choice == '3':
                await handle_system_config(proxy_manager)
            
            elif choice == '4':
                if get_yes_no_input("\n[yellow]Bạn có chắc muốn thoát? (y/n): [/yellow]"):
                    clear_screen()
                    show_header()
                    console.print("\n[green]Cảm ơn bạn đã sử dụng Proxy Master Suite![/green]")
                    await asyncio.sleep(1)
                    break
            
            else:
                console.print("[red]Lựa chọn không hợp lệ![/red]")
                await asyncio.sleep(1)

        elif choice == '2':
            await get_free_proxies_async()
                
        elif choice == '3':
            try:
                show_config_menu()
                config = load_config()
            except Exception as e:
                console.print(f"[red]Lỗi khi cấu hình: {str(e)}[/red]")
                await asyncio.sleep(1)
                
        elif choice == '4':
            farewell_text = create_rainbow_text("◆ TẠM BIỆT VÀ HẸN GẶP LẠI ◆")
            console.print("\n" + farewell_text)
            console.print("\n[italic bright_white]Cảm ơn bạn đã sử dụng công cụ![/italic bright_white]")
            await asyncio.sleep(1)
            return
        else:
            if config.get('use_rich_interface', True):
                console.print("[bold bright_red]◆ Lựa chọn không hợp lệ. Vui lòng chọn 1-4 ◆[/bold bright_red]")
                console.input("[bold bright_cyan]◆ Nhấn Enter để tiếp tục...[/bold bright_cyan]")
            else:
                print(f"\n{Fore.RED}{Style.BRIGHT}Lựa chọn không hợp lệ. Vui lòng chọn 1-4.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Nhấn Enter để tiếp tục...{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        # Kiểm tra Python version
        if sys.version_info < (3, 7):
            console.print("[red]Error: Python 3.7 or higher is required[/red]")
            sys.exit(1)

        # Kiểm tra và cài đặt dependencies
        if not os.path.exists(os.path.join(os.path.dirname(__file__), '.deps_checked')):
            check_and_install_dependencies()
            with open(os.path.join(os.path.dirname(__file__), '.deps_checked'), 'w') as f:
                f.write('')

        # Chạy chương trình chính
        try:
            asyncio.run(main())
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                # Xử lý lỗi event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(main())
                loop.close()
            else:
                raise

    except KeyboardInterrupt:
        console.print("\n[yellow]Đã hủy thao tác![/yellow]")
    except Exception as e:
        console.print(f"\n[red]Lỗi không mong muốn: {str(e)}[/red]")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
    finally:
        try:
            # Dọn dẹp tài nguyên
            for task in asyncio.all_tasks():
                task.cancel()
        except:
            pass
        console.print("[green]Cảm ơn bạn đã sử dụng tool![/green]")