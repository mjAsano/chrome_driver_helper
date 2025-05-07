# Chrome Driver Helper

`ChromeDriverHelper`는 [Selenium WebDriver](https://www.selenium.dev/)를 기반으로 크롬 브라우저를 제어하며 웹 자동화를 간편하게 수행할 수 있도록 도와주는 고급 유틸리티 클래스입니다. 
봇 감지 우회, 네트워크 모니터링, 파일 다운로드, 쿠키 제어 등 다양한 기능을 제공합니다.

---

## 주요 기능

* 헤드리스 모드 지원 (`--headless=new`)
* 프록시 서버 연결 지원
* 자동 재시도 로직 포함
* 네트워크 요청 모니터링
* 봇 감지 우회 설정 (navigator 속성 조작 등)
* 페이지 분석 및 메타정보 수집
* 파일 다운로드 (네트워크 로그 기반 파일 탐색 포함)
* 스크린샷 저장
* 쿠키 수집/추가/삭제 기능
* 자바스크립트 코드 실행
* CPU, 메모리 사용량 확인

---

## 설치 방법

Python 패키지 설치:

```bash
pip install selenium requests psutil
```

추가로 Chrome 브라우저와 ChromeDriver가 시스템에 설치되어 있어야 합니다.

### macOS (Intel/M1/M2)

```bash
brew install --cask google-chrome
brew install chromedriver
```

환경변수 설정 (필요한 경우):

```bash
export CHROMEDRIVER_PATH_MAC_ARM="/opt/homebrew/bin/chromedriver"
export CHROME_BINARY_MAC="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

### Linux (Ubuntu 예시)

```bash
sudo apt update
sudo apt install -y chromium-browser chromium-chromedriver
```

환경변수 설정:

```bash
export CHROME_BINARY_LINUX="/usr/bin/chromium-browser"
```

### Windows

1. [Chrome 브라우저 설치](https://www.google.com/chrome/)
2. [ChromeDriver 다운로드](https://sites.google.com/chromium.org/driver/)
   Chrome 브라우저 버전에 맞는 드라이버를 다운로드하고 압축 해제한 후, `chromedriver.exe` 파일의 경로를 확인합니다.

환경변수에 경로를 추가하거나 코드에서 명시적으로 경로 설정:

```python
os.environ['CHROMEDRIVER_PATH'] = r'C:\path\to\chromedriver.exe'
```

---

## 사용 예시

```python
from chrome_driver_helper import ChromeDriverHelper

# 기본 설정으로 초기화
helper = ChromeDriverHelper(headless=True)

# 웹사이트 열기
helper.driver.get("https://example.com")

# 페이지 정보 분석
info = helper.analyze_page()
print(info)

# 스크린샷 저장
helper.take_screenshot("screenshot.png")

# 네트워크 트래픽 10초간 모니터링
logs = helper.monitor_network(duration=10)

# 쿠키 수집 및 추가
cookies = helper.get_cookies()
helper.add_cookie({"name": "sample", "value": "test"})

# 종료
helper.close()
```

---

## 주요 메서드

| 메서드                                        | 설명                 |
| ------------------------------------------ | ------------------ |
| `get_chrome_driver()`                      | Chrome 드라이버 초기화    |
| `analyze_page()`                           | 현재 페이지의 요소 분석      |
| `monitor_network(duration)`                | 네트워크 요청 모니터링       |
| `find_downloadable_files()`                | 다운로드 가능한 파일 URL 추출 |
| `take_screenshot(path)`                    | 스크린샷 저장            |
| `execute_script(js)`                       | 자바스크립트 실행          |
| `add_cookie(cookie)` / `add_cookies(list)` | 쿠키 추가              |
| `get_cookies()`                            | 현재 쿠키 목록 가져오기      |
| `delete_all_cookies()`                     | 모든 쿠키 삭제           |
| `wait_for_element(by, value)`              | 특정 요소 로딩까지 대기      |
| `wait_for_page_load()`                     | 페이지 로딩 완료 대기       |
| `get_browser_stats()`                      | 브라우저 자원 사용량 확인     |
| `close()`                                  | 드라이버 종료 및 정리       |

---

## 시스템 요구사항

* Python 3.6 이상
* Google Chrome
* ChromeDriver
* selenium, requests, psutil

---

## 주의사항

* 헤드리스 모드에서는 일부 사이트가 자동화를 감지할 수 있습니다.
* 프록시 서버가 불안정하면 요청 실패가 발생할 수 있습니다.
* 네트워크 모니터링은 메모리 사용량 증가로 이어질 수 있습니다.

---

## 라이선스

MIT License

