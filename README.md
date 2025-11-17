# 📊 서울시 범죄율, 1인가구 및 CCTV 상관관계 분석

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

## 1. 프로젝트 주제
**"범죄율 및 1인 가구 증가와 CCTV 설치 현황의 상관관계 분석"**

서울시 공공데이터를 활용하여 자치구별 범죄 발생, CCTV 설치, 1인가구 밀집도 데이터를 병합하고, 이들 간의 유의미한 상관관계를 시각적으로 분석한 **Streamlit 웹 애플리케이션**입니다.

---

## 2. 주제 선정 이유
이 프로젝트는 다음과 같은 사회적 궁금증을 데이터로 확인해보고자 시작되었습니다.

* **"CCTV가 많이 설치된 지역은 정말로 범죄가 적을까?"**
* **"1인가구가 많은 지역은 범죄에 더 취약할까?"**

단순한 통계 나열을 넘어, 실제 데이터를 통해 상관관계를 규명하고 시각화하는 것을 목표로 했습니다.

---

## 3. 주요 분석 내용 및 기능
이 앱은 총 4가지의 분석 페이지를 제공합니다.

### 🚨 1) 범죄 분석
* **기능:** 연도별, 범죄 유형(절도, 살인 등), 구분(발생/검거) 필터링 제공
* **내용:** 선택한 조건에 따른 자치구별 범죄 건수를 막대그래프로 시각화하여 특정 지역(예: 강남구)의 범죄 빈도를 파악

### 📹 2) CCTV 분석
* **기능:** '범죄예방 수사용' CCTV 데이터 활용
* **내용:** 연도별 자치구 CCTV 설치 총 대수를 내림차순화** |
| **김현하** | 자료 조사 |

---

## 7. 실행 방법 (How to run)

### 필요 라이브러리 설치
```bash
pip install streamlit pandas seaborn matplotlib openpyxl
앱 실행

streamlit run app.py
```

---

## 8. 회고 및 배운 점
데이터 전처리: .csv와 .xlsx 등 서로 다른 형식의 공공데이터를 자치구 기준으로 정제하고 병합(Merge)하는 과정을 통해 데이터 핸들링 능력을 키웠습니다.

생성형 AI 활용: 복잡한 전처리 로직 작성 시 AI의 도움을 받아 개발 효율을 높이는 경험을 했습니다.

시각화의 중요성: 데이터를 표로 볼 때보다 시각화했을 때 상관관계를 훨씬 직관적으로 이해할 수 있음을 체감했습니다.
