import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Advanced DCF Model", layout="wide")

st.title("📊 실무형 동적 DCF Valuation 모델")

# 1. 초기 가정 입력
st.sidebar.header("Global Assumptions")
wacc = st.sidebar.slider("WACC (%)", 5.0, 15.0, 8.0) / 100
terminal_growth = st.sidebar.slider("Terminal Growth (%)", 0.0, 5.0, 1.0) / 100
net_debt = st.sidebar.number_input("순부채 (억 원)", value=500)
shares = st.sidebar.number_input("발행 주식 수 (만 주)", value=10000)

# 2. 연도별 데이터 직접 입력 (Editor)
st.subheader("연도별 FCF 및 성장률 설정 (표를 클릭해 수정하세요)")
default_data = {
    "연도": [1, 2, 3, 4, 5],
    "성장률(%)": [10.0, 8.0, 6.0, 4.0, 2.0],
    "기초 FCF(억 원)": [1000, 0, 0, 0, 0] # 1년차 이후는 성장률로 자동계산
}
df_input = pd.DataFrame(default_data)
# 데이터 에디터 생성
df_edited = st.data_editor(df_input, use_container_width=True)

# 3. 로직 계산
fcf_values = []
curr = df_edited.loc[0, "기초 FCF(억 원)"]
for i in range(5):
    if i > 0:
        curr = fcf_values[i-1] * (1 + df_edited.loc[i, "성장률(%)"] / 100)
    fcf_values.append(curr)

df_results = pd.DataFrame({
    "연도": df_edited["연도"],
    "성장률": df_edited["성장률(%)"],
    "추정 FCF": fcf_values
})
df_results["PV(현재가치)"] = df_results["추정 FCF"] / ((1 + wacc) ** df_results["연도"])

# 터미널 가치 계산
tv = (fcf_values[-1] * (1 + terminal_growth)) / (wacc - terminal_growth)
tv_pv = tv / ((1 + wacc) ** 5)
enterprise_value = df_results["PV(현재가치)"].sum() + tv_pv
equity_value = enterprise_value - net_debt
price = (equity_value * 100000000) / (shares * 10000)

# 4. 결과 출력
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.write("### 계산 결과")
    st.dataframe(df_results)
with col2:
    st.metric("기업가치(EV)", f"{enterprise_value:,.0f} 억 원")
    st.metric("주당 가치", f"{price:,.0f} 원")
    st.info(f"Terminal Value (PV): {tv_pv:,.0f} 억 원")