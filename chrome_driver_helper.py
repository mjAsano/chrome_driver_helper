import os
import platform
import logging
import json
import time
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from typing import Optional, List, Dict, Union, Any
import base64
import psutil
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChromeDriverHelper:
    def __init__(self, headless=True, proxy: Optional[str] = None, timeout: int = 30):
        self.headless = headless
        self.proxy = proxy
        self.timeout = timeout
        self.driver = None
        self.network_logs = []
        self.retry_count = 3
        self.retry_delay = 2
        self.browser_stats = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'network_requests': 0,
            'errors': 0
        }
        logger.info(f"ChromeDriverHelper initialized with headless={headless}, proxy={proxy}, timeout={timeout}")
        # 자동으로 드라이버 초기화
        self.get_chrome_driver()

    def _ensure_driver(self):
        """드라이버가 초기화되어 있는지 확인하고, 없다면 초기화합니다."""
        if self.driver is None:
            logger.info("Driver not initialized. Initializing now...")
            self.get_chrome_driver()
        return self.driver

    def get_chrome_driver(self):
        """Chrome 드라이버를 초기화하고 반환합니다."""
        if self.driver is not None:
            return self.driver

        logger.info("Starting to setup Chrome driver...")
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")  # 새로운 헤드리스 모드 사용
            logger.info("Headless mode enabled")
        
        # 기본 설정
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 성능 최적화 설정
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        chrome_options.add_argument("--disable-site-isolation-trials")
        
        # 메모리 최적화
        chrome_options.add_argument("--disable-application-cache")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-breakpad")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-domain-reliability")
        chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # 봇 감지 우회 설정 강화
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # User-Agent 설정
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        # 추가 봇 감지 우회 옵션
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # 프록시 설정
        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')
            logger.info(f"Proxy configured: {self.proxy}")
        
        # 네트워크 로깅 설정
        chrome_options.set_capability("goog:loggingPrefs", {
            "performance": "ALL",
            "browser": "ALL",
            "network": "ALL"
        })
        
        system = platform.system()
        machine = platform.machine()
        logger.info(f"System: {system}, Machine: {machine}")

        if system == "Linux":
            chrome_options.binary_location = os.getenv('CHROME_BINARY_LINUX', '/usr/bin/chromium')
            service = Service("/usr/bin/chromedriver")
        elif system == "Darwin":  # macOS
            chrome_options.binary_location = os.getenv('CHROME_BINARY_MAC', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
            if machine == "arm64":  # M1/M2 Mac
                chromedriver_path = os.getenv('CHROMEDRIVER_PATH_MAC_ARM', '/opt/homebrew/bin/chromedriver')
            else:
                chromedriver_path = os.getenv('CHROMEDRIVER_PATH_MAC_INTEL', '/usr/local/bin/chromedriver')
            logger.info(f"Using ChromeDriver path: {chromedriver_path}")
            if not os.path.exists(chromedriver_path):
                error_msg = f"ChromeDriver not found at {chromedriver_path}. Try installing with: brew install chromedriver"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            service = Service(chromedriver_path)
        else:  # Windows or other
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())

        for attempt in range(self.retry_count):
            try:
                logger.info(f"Creating Chrome driver instance (attempt {attempt + 1}/{self.retry_count})...")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # 웹드라이버 속성 제거
                self._remove_webdriver_attributes()
                
                # 타임아웃 설정
                self.driver.set_page_load_timeout(self.timeout)
                self.driver.set_script_timeout(self.timeout)
                
                logger.info("Chrome driver created successfully")
                return self.driver
                
            except WebDriverException as e:
                logger.error(f"Failed to create Chrome driver (attempt {attempt + 1}/{self.retry_count}): {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def _remove_webdriver_attributes(self):
        """웹드라이버 속성을 제거하는 스크립트를 실행합니다."""
        scripts = [
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
            "Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko', 'en-US', 'en']})",
            "Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'})",
            "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8})",
            "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8})",
            "Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'})"
        ]
        
        for script in scripts:
            try:
                self.driver.execute_script(script)
            except Exception as e:
                logger.warning(f"Failed to execute script: {script}, Error: {str(e)}")

    def execute_script(self, script: str, *args) -> Any:
        """JavaScript를 실행합니다."""
        driver = self._ensure_driver()
        try:
            return driver.execute_script(script, *args)
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            raise

    def get_page_source(self) -> str:
        """현재 페이지의 소스를 가져옵니다."""
        driver = self._ensure_driver()
        return driver.page_source

    def analyze_page(self) -> Dict[str, Any]:
        """현재 페이지를 분석합니다."""
        driver = self._ensure_driver()
        analysis = {
            'title': driver.title,
            'url': driver.current_url,
            'cookies': len(driver.get_cookies()),
            'scripts': len(driver.find_elements(By.TAG_NAME, "script")),
            'images': len(driver.find_elements(By.TAG_NAME, "img")),
            'links': len(driver.find_elements(By.TAG_NAME, "a")),
            'forms': len(driver.find_elements(By.TAG_NAME, "form")),
            'iframes': len(driver.find_elements(By.TAG_NAME, "iframe")),
            'meta_tags': len(driver.find_elements(By.TAG_NAME, "meta"))
        }
        return analysis

    def get_browser_stats(self) -> Dict[str, float]:
        """브라우저의 현재 상태를 반환합니다."""
        driver = self._ensure_driver()
        process = psutil.Process(driver.service.process.pid)
        
        self.browser_stats.update({
            'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
            'cpu_usage': process.cpu_percent(),
            'network_requests': len(self.network_logs),
            'errors': self.browser_stats['errors']
        })
        
        return self.browser_stats

    def get_network_logs(self):
        """네트워크 로그를 가져옵니다."""
        logs = self.driver.get_log('performance')
        network_logs = []
        
        for log in logs:
            try:
                log_entry = json.loads(log['message'])['message']
                if 'Network.response' in log_entry['method'] or 'Network.request' in log_entry['method']:
                    network_logs.append(log_entry)
            except:
                continue
                
        return network_logs

    def download_file(self, url, save_path=None):
        """URL에서 파일을 다운로드합니다."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            if save_path is None:
                # URL에서 파일명 추출
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    filename = f"downloaded_file_{int(time.time())}"
                save_path = filename
            
            # 파일 저장
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"File downloaded successfully to {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return None

    def monitor_network(self, duration=10):
        """지정된 시간 동안 네트워크 트래픽을 모니터링합니다."""
        logger.info(f"Starting network monitoring for {duration} seconds...")
        start_time = time.time()
        self.network_logs = []
        
        while time.time() - start_time < duration:
            logs = self.get_network_logs()
            self.network_logs.extend(logs)
            time.sleep(1)
        
        logger.info(f"Network monitoring completed. Captured {len(self.network_logs)} network events")
        return self.network_logs

    def find_downloadable_files(self, file_extensions=None):
        """모니터링된 네트워크 로그에서 다운로드 가능한 파일 URL을 찾습니다."""
        if file_extensions is None:
            file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.mp4', '.mp3']
        
        downloadable_urls = []
        for log in self.network_logs:
            try:
                if 'Network.response' in log['method']:
                    url = log['params']['response']['url']
                    if any(url.lower().endswith(ext) for ext in file_extensions):
                        downloadable_urls.append(url)
            except:
                continue
        
        return downloadable_urls

    def take_screenshot(self, save_path: Optional[str] = None) -> Optional[str]:
        """현재 페이지의 스크린샷을 찍습니다."""
        try:
            driver = self._ensure_driver()
            if save_path is None:
                save_path = f"screenshot_{int(time.time())}.png"
            
            driver.save_screenshot(save_path)
            logger.info(f"Screenshot saved to {save_path}")
            return save_path
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return None

    def add_cookie(self, cookie: Dict, url: Optional[str] = None):
        """쿠키를 추가합니다.
        
        Args:
            cookie (Dict): 추가할 쿠키 정보
            url (Optional[str]): 쿠키를 추가할 도메인의 URL. None이면 현재 URL 사용
        """
        driver = self._ensure_driver()
        try:
            # URL이 제공된 경우 해당 URL로 이동
            if url:
                driver.get(url)
                time.sleep(1)  # 페이지 로딩 대기
            
            # 쿠키에 필수 필드 추가
            if 'domain' not in cookie and driver.current_url:
                cookie['domain'] = urlparse(driver.current_url).netloc
            
            if 'path' not in cookie:
                cookie['path'] = '/'
            
            driver.add_cookie(cookie)
            logger.info(f"Cookie added successfully: {cookie['name']}")
        except Exception as e:
            logger.error(f"Error adding cookie: {str(e)}")
            self.browser_stats['errors'] += 1
            raise

    def add_cookies(self, cookies: List[Dict], url: Optional[str] = None):
        """여러 쿠키를 한 번에 추가합니다.
        
        Args:
            cookies (List[Dict]): 추가할 쿠키 목록
            url (Optional[str]): 쿠키를 추가할 도메인의 URL. None이면 현재 URL 사용
        """
        driver = self._ensure_driver()
        try:
            # URL이 제공된 경우 해당 URL로 이동
            if url:
                driver.get(url)
                time.sleep(1)  # 페이지 로딩 대기
            
            current_domain = urlparse(driver.current_url).netloc
            
            for cookie in cookies:
                # 쿠키에 필수 필드 추가
                if 'domain' not in cookie:
                    cookie['domain'] = current_domain
                if 'path' not in cookie:
                    cookie['path'] = '/'
                
                driver.add_cookie(cookie)
                logger.info(f"Cookie added successfully: {cookie['name']}")
        except Exception as e:
            logger.error(f"Error adding cookies: {str(e)}")
            self.browser_stats['errors'] += 1
            raise

    def get_cookies(self) -> List[Dict]:
        """현재 세션의 모든 쿠키를 가져옵니다."""
        driver = self._ensure_driver()
        try:
            cookies = driver.get_cookies()
            logger.info(f"Retrieved {len(cookies)} cookies")
            return cookies
        except Exception as e:
            logger.error(f"Error getting cookies: {str(e)}")
            self.browser_stats['errors'] += 1
            raise

    def delete_all_cookies(self):
        """모든 쿠키를 삭제합니다."""
        driver = self._ensure_driver()
        try:
            driver.delete_all_cookies()
            logger.info("All cookies deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting cookies: {str(e)}")
            self.browser_stats['errors'] += 1
            raise

    def wait_for_element(self, by, value, timeout: Optional[int] = None):
        """특정 요소가 나타날 때까지 기다립니다."""
        driver = self._ensure_driver()
        if timeout is None:
            timeout = self.timeout
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {value}")
            self.browser_stats['errors'] += 1
            raise

    def wait_for_page_load(self, timeout: Optional[int] = None):
        """페이지가 완전히 로드될 때까지 기다립니다."""
        driver = self._ensure_driver()
        if timeout is None:
            timeout = self.timeout
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except TimeoutException:
            logger.warning(f"Page load timeout after {timeout} seconds")
            self.browser_stats['errors'] += 1
            raise

    def close(self):
        """드라이버를 종료합니다."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing driver: {str(e)}")
            finally:
                self.driver = None
                logger.info("Chrome driver closed")

