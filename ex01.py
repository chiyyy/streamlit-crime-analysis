import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings


# 경고 메시지 무시
warnings.filterwarnings('ignore')
# 한글 폰트 설정
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

# Streamlit 페이지 기본 설정
st.set_page_config(
    page_title="🗺️ 서울시 데이터 분석",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 서울시 데이터 분석 프로젝트")


# @st.cache_data : 데이터를 캐시에 저장해두고, 변경 없을 시 재로딩 안함 (속도 향상)
@st.cache_data
def load_crime_data():
    data = pd.read_csv("crime_data_tidy.csv", encoding='utf-8-sig')
    # 소계 제외한 실제 범죄 유형 리스트
    crime_types_no_total = data[data['범죄유형'] != '소계']['범죄유형'].unique()
    return data, crime_types_no_total

@st.cache_data
def load_cctv_data(gu_list):
    # 3번째 줄에 헤더가 있으므로 header=2 옵션을 사용
    data = pd.read_excel("서울시 자치구 (범죄예방 수사용) CCTV 설치현황_241231.xlsx", header=2)

    # 데이터 전처리
    # 구분 컬럼을 '자치구'로 이름 변경
    data = data.rename(columns={'구분': '자치구'})
    
    # 범죄 데이터에 있는 자치구 리스트로 필터링
    data = data[data['자치구'].isin(gu_list)]
    
    # 연도 컬럼들 숫자형으로 변경
    year_cols = [col for col in data.columns if '년' in col]
    for col in year_cols:
        # 콤마 제거 후 숫자 변환
        data[col] = pd.to_numeric(data[col].astype(str).str.replace(',', ''), errors='coerce')
        
    # 필요한 컬럼만 선택 (자치구 + 연도별 데이터)
    data = data[['자치구'] + year_cols]
    return data

@st.cache_data
def load_population_data():
    data = pd.read_csv("1인가구정보.csv", header=1, encoding='utf-8-sig')
    # '합계' 행 제거
    data = data[data['동별(1)'] != '합계']
    # 컬럼 이름 변경
    data = data.rename(columns={'동별(1)': '자치구', '1인세대': '1인가구', '전체세대': '전체세대'})
    # 숫자형으로 변경
    data['1인가구'] = pd.to_numeric(data['1인가구'], errors='coerce')
    data['전체세대'] = pd.to_numeric(data['전체세대'], errors='coerce')
    # 자치구별로 합계 계산
    gu_pop = data.groupby('자치구', as_index=False).agg(
        전체세대_합= ('전체세대', 'sum'),
        일인가구_합= ('1인가구', 'sum')
    )
    # 1인가구 비율 계산
    gu_pop['1인가구_비율(%)'] = (gu_pop['일인가구_합'] / gu_pop['전체세대_합']) * 100
    return gu_pop


def show_common(merged_data):
    """
    공통 분석 페이지
    merge 한 데이터프레임을 받아서 시각화만 담당
    """
    st.header("🤝 공통 분석 (상관관계)")
    st.write("CCTV 총대수, 1인가구 정보, 그리고 **'2020년 총 범죄 발생 건수'** 간의 상관관계를 분석합니다.")
    st.write("X축과 Y축을 선택해 산점도(scatterplot)를 확인합니다.")

    # --- X, Y축 선택 ---
    # 분석할 컬럼 리스트 (자치구 제외)
    analysis_cols = [col for col in merged_data.columns if col != '자치구']

    # X축, Y축 선택창을 가로로 나란히 배치
    col_x, col_y = st.columns(2)
    with col_x:
        x_axis = st.selectbox("X축을 선택하세요", analysis_cols, index=0)
    with col_y:
        # Y축은 X축에서 선택한 것을 제외
        y_axis_options = [col for col in analysis_cols if col != x_axis]
        
        y_axis = st.selectbox("Y축을 선택하세요", y_axis_options, index=0)

    st.divider() # --- 구분선 ---

    # --- 시각화 (Seaborn Scatterplot) ---
    st.subheader(f"📊 '{x_axis}'와 '{y_axis}' 간의 산점도")
    fig = plt.figure(figsize=(10, 6))
    sns.scatterplot(data=merged_data, x=x_axis, y=y_axis)
    plt.title(f"'{x_axis}'와 '{y_axis}' 간의 상관관계 (산점도)")
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    st.pyplot(fig)

    # --- 상관계수 표시 ---
    correlation = merged_data[x_axis].corr(merged_data[y_axis])
    st.markdown(f"### 📈 두 변수의 상관계수: **{correlation:.4f}**")

    if abs(correlation) > 0.5:
          st.success(f"상관계수 절댓값이 0.5 이상으로, 두 변수 간에 **강한 관계**가 보입니다.")
    elif abs(correlation) > 0.2:
          st.info(f"상관계수 절댓값이 0.2~0.5 사이로, **약한 관계**가 보입니다.")
    else:
          st.warning(f"상관계수 절댓값이 0.2 미만으로, 두 변수 간의 관계가 매우 약하거나 거의 없습니다.")

    # --- 참고용 통합 데이터 ---
    st.subheader("참고: 상관관계 분석용 통합 데이터")
    st.dataframe(merged_data)


def show_crime(crime_data, crime_types):
    """범죄 분석 페이지: 조건별 범죄 건수 시각화"""
    st.header("🚨 범죄 분석")
    st.subheader("조건별 범죄 건수 (자치구별)")
    st.write("연도, 범죄유형, 구분을 선택하여 자치구별 건수를 확인합니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_year = st.selectbox("연도를 선택하세요", sorted(crime_data['연도'].unique(), reverse=True))
    with col2:
        selected_crime = st.selectbox("범죄유형을 선택하세요", crime_types)
    with col3:
        selected_type = st.selectbox("구분을 선택하세요", crime_data['구분'].unique())

    # 선택한 기준으로 데이터 필터링
    filtered_data = crime_data[
        (crime_data['연도'] == selected_year) &
        (crime_data['범죄유형'] == selected_crime) &
        (crime_data['구분'] == selected_type)
    ]

    st.divider() # --- 구분선 ---

    st.write(f"**{selected_year}년 | {selected_crime} | {selected_type}** 건수 데이터")

    # '건수' 기준으로 내림차순 정렬
    plot_data = filtered_data.sort_values('건수', ascending=False)
    st.dataframe(plot_data[['자치구', '건수']])

    # --- 시각화 (Seaborn Barplot) ---
    st.subheader("📊 자치구별 건수 비교")
    fig = plt.figure(figsize=(12, 6))
    sns.barplot(data=plot_data, x='자치구', y='건수')
    plt.title(f"{selected_year}년 {selected_crime} ({selected_type}) 건수")
    plt.xticks(rotation=90) # 자치구 이름이 길어서 90도 회전
    st.pyplot(fig)

def show_cctv(cctv_data):
    """CCTV 분석 페이지: (수정됨) 연도별 CCTV 대수 시각화"""
    # 새 데이터에 맞게 헤더 제목 변경
    st.header("📹 CCTV 분석 (범죄예방 수사용)")
    st.subheader("연도별 CCTV 설치 현황 (자치구별)")
    

    # cctv_data 컬럼에서 '자치구'를 제외한 리스트 (연도 리스트)
    year_list = [col for col in cctv_data.columns if col != '자치구']
    # 연도를 최신순으로 정렬하여 선택
    selected_year = st.selectbox("조회할 연도를 선택하세요", sorted(year_list, reverse=True))

    st.divider() # --- 구분선 ---

    st.write(f"**'{selected_year}'** 기준 자치구별 CCTV 총 대수")

    # 'selected_year' 컬럼을 기준으로 내림차순 정렬
    plot_data = cctv_data[['자치구', selected_year]].sort_values(selected_year, ascending=False)
    # 그래프를 그리기 위해 컬럼 이름을 'CCTV 대수'로 통일
    plot_data = plot_data.rename(columns={selected_year: 'CCTV 대수'})
    
    st.dataframe(plot_data)

    # --- 시각화 (Seaborn Barplot) ---
    st.subheader(f"📊 {selected_year}년 자치구별 CCTV 대수 비교")
    fig = plt.figure(figsize=(12, 6))
    sns.barplot(data=plot_data, x='자치구', y='CCTV 대수') # y축을 'CCTV 대수'로 변경
    plt.title(f"'{selected_year}' 범죄예방 수사용 CCTV 자치구별 총 대수")
    plt.xticks(rotation=90)
    st.pyplot(fig)

def show_population(pop_data):
    st.header("👤 1인가구 정보 분석")
    st.subheader("자치구별 1인가구 현황")

    analysis_options = ['1인가구 수 (절대값)', '전체 세대 대비 1인가구 비율 (%)']
    selected_analysis = st.selectbox("분석할 항목을 선택하세요", analysis_options)

    st.divider() # --- 구분선 ---

    if selected_analysis == '1인가구 수 (절대값)':
        plot_data = pop_data.sort_values('일인가구_합', ascending=False)
        y_col = '일인가구_합'
        title = '자치구별 1인가구 수'
    else:
        plot_data = pop_data.sort_values('1인가구_비율(%)', ascending=False)
        y_col = '1인가구_비율(%)'
        title = '자치구별 1인가구 비율 (%)'

    st.write(f"**{title}** (내림차순 정렬)")
    st.dataframe(plot_data[['자치구', y_col]])

    # --- 시각화 (Seaborn Barplot) ---
    st.subheader(f"📊 {title} 그래프")
    fig = plt.figure(figsize=(12, 6))
    sns.barplot(data=plot_data, x='자치구', y=y_col)
    plt.title(title)
    plt.xticks(rotation=90)
    st.pyplot(fig)

# 데이터 로드
crime_df, crime_types_no_total = load_crime_data()
# 범죄 데이터의 자치구 리스트를 CCTV 로딩 시 전달
gu_list = crime_df['자치구'].unique()
cctv_df = load_cctv_data(gu_list)
pop_df = load_population_data()


# 1. CCTV (자치구별 합계)

if '2020년' in cctv_df.columns:
    cctv_sum = cctv_df[['자치구', '2020년']].rename(columns={'2020년': 'CCTV 총대수(2020년)'})
else:
    # '2020년' 데이터가 없는 경우, 빈 데이터프레임 대신
    # 가장 최신 연도 컬럼을 사용하거나 0으로 채움
    # gu_list로 빈 데이터프레임을 만들기
    st.warning("CCTV 데이터에 '2020년' 컬럼이 없어 상관분석이 정확하지 않을 수 있습니다.")
    cctv_sum = pd.DataFrame({'자치구': gu_list, 'CCTV 총대수(2020년)': 0})

# 예: 가장 최신 연도(2020)의 '소계'(총 범죄), '발생' 건수
crime_for_merge = crime_df[
    (crime_df['연도'] == 2020) &
    (crime_df['범죄유형'] == '소계') &
    (crime_df['구분'] == '발생')
]
# 병합을 위해 컬럼 이름 변경
crime_col_name = "2020_총범죄_발생건수"
crime_for_merge = crime_for_merge[['자치구', '건수']].rename(columns={'건수': crime_col_name})

# (CCTV + 1인가구)
merged_df = pd.merge(cctv_sum, pop_df, on='자치구', how='left')
# + 범죄
final_merged_df = pd.merge(merged_df, crime_for_merge, on='자치구', how='left')
# (혹시 모를 결측치 0으로 채우기)
final_merged_df = final_merged_df.fillna(0)


st.sidebar.title("🌟 서울시 데이터 분석")
menu = ["공통 분석", "범죄 분석", "CCTV 분석", "1인가구 정보 분석"]
selected = st.sidebar.selectbox("메뉴를 선택하세요", menu)

if selected == "공통 분석":
    # 'final_merged_df'를 함수에 전달
    show_common(final_merged_df)
elif selected == "범죄 분석":
    # 전체 범죄 데이터와 범죄 유형 리스트를 함수에 전달
    show_crime(crime_df, crime_types_no_total)
elif selected == "CCTV 분석":
    # 전체 CCTV 데이터를 함수에 전달
    show_cctv(cctv_df)
elif selected == "1인가구 정보 분석":
    # 자치구별 1인가구 데이터를 함수에 전달
    show_population(pop_df)