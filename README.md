# Chrome Driver Helper

Chrome Driver Helper는 Selenium WebDriver를 사용하여 웹 자동화를 더 쉽게 구현할 수 있도록 도와주는 유틸리티 클래스입니다.

## 주요 기능

- 헤드리스 모드 지원
- 프록시 설정 지원
- 자동 재시도 메커니즘
- 네트워크 모니터링
- 쿠키 관리
- 스크린샷 캡처
- 파일 다운로드
- 브라우저 상태 모니터링
- 봇 감지 우회 기능

## 설치 방법

```bash
pip install selenium requests psutil
```

Chrome 브라우저와 ChromeDriver가 시스템에 설치되어 있어야 합니다.

### macOS 설치
```bash
brew install chromedriver
```

## 사용 예시

```python
from chrome_driver_helper import ChromeDriverHelper

# 기본 설정으로 초기화
helper = ChromeDriverHelper(headless=True)

# 웹사이트 방문
helper.driver.get("https://example.com")

# 페이지 분석
analysis = helper.analyze_page()
print(analysis)

# 스크린샷 캡처
helper.take_screenshot("screenshot.png")

# 네트워크 모니터링
network_logs = helper.monitor_network(duration=10)

# 쿠키 관리
cookies = helper.get_cookies()
helper.add_cookie({"name": "test", "value": "value"})

# 브라우저 종료
helper.close()
```

## 주요 메서드

- `get_chrome_driver()`: Chrome 드라이버 초기화
- `analyze_page()`: 현재 페이지 분석
- `monitor_network()`: 네트워크 트래픽 모니터링
- `take_screenshot()`: 스크린샷 캡처
- `download_file()`: 파일 다운로드
- `get_cookies()`, `add_cookie()`, `delete_all_cookies()`: 쿠키 관리
- `wait_for_element()`: 특정 요소 대기
- `wait_for_page_load()`: 페이지 로드 대기

## 시스템 요구사항

- Python 3.6 이상
- Chrome 브라우저
- ChromeDriver
- selenium
- requests
- psutil

## 주의사항

- 헤드리스 모드에서는 일부 웹사이트가 봇 감지를 할 수 있습니다.
- 프록시 사용 시 프록시 서버의 안정성을 확인하세요.
- 네트워크 모니터링은 메모리 사용량에 영향을 줄 수 있습니다.

## 라이선스

MIT License 
