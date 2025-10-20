import os
from longsea import al
from openpyxl import load_workbook
import streamlit as st
import pandas as pd
import zipfile
import io

# ----------------------------------------------------------------------------------------------------------------------
# 设置页面信息
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# 设置网页显示信息
st.set_page_config(page_title="汇总工作表_2025",layout="centered", page_icon=":soon_arrow:",initial_sidebar_state="expanded",)
# 添加侧边栏说明文本
st.sidebar.write("txt_A")

# st.write("***")
st.markdown("### 🚩:red[拆分成绩表]")
st.markdown("***")

# 创建一个上传文件的按钮
uploaded_file = st.file_uploader("上传年级成绩总表", type=["xlsx"])

# 读取工作薄为一个df对象
if not uploaded_file:
    st.text_area(label='设置说明', value="将一个《级段成绩总表》拆为：《班级成绩表》、《班级_学科成绩表》、《学科成绩表》", height=80)
    exit()
elif uploaded_file:
    df = pd.read_excel(uploaded_file, engine='openpyxl')  # 读取所有工作表。
if st.checkbox(label='显示表',value= True):
       st.dataframe(df.head(3),use_container_width= True)

# ===============================================================================
# 将年级总表按班级进行分组，生成班级数据
gp = df.astype({'班级': 'str'}).groupby(by='班级')  # 强制转换班级列为字符串
dfs_dic_cls = {name: ite for name, ite in gp}
# 将分组数据保存为zip文件
zp_cls = al.dfs_to_zip(dfs_dic_cls, format='excel')

# =================================================================================
# 将每班数据按学科进行分组
dfs_cls_sub = {}
for cls, ite in dfs_dic_cls.items():
    dfs =al.df_split_column(ite, ['语文', '数学', '英语','物理','化学','生物','政治','历史','地理'])
    for sub,it in dfs.items():
        dfs_cls_sub[cls +'_'+ sub] = it
# 将分班分学科数据保存为zip文件
zp_cls_sub = al.dfs_to_zip(dfs_cls_sub, format='excel')

# ===================================================================================
# 将年级总表按学科进行拆分，
dfs_sub =al.df_split_column(df, ['语文', '数学', '英语','物理','化学','生物','政治','历史','地理'])
# 将分学科数据保存为zip文件
zp_sub = al.dfs_to_zip(dfs_sub, format='excel')

# ===================================================================================
st.markdown("***")
col_A, col_B,col_C = st.columns(3)
with col_A:
    # 创建下载按钮
    st.download_button(
        label='下载"班级"成绩表',
        data=zp_cls,
        file_name="班级成绩表.zip",
        mime='application/zip',        # 修正MIME类型为ZIP
        type='primary',
        use_container_width=True
    )
with col_B:
    # 创建下载按钮
    st.download_button(
        label='下载"班级_学科"成绩表',
        data=zp_cls_sub,
        file_name="班级_学科成绩表.zip",
        mime='application/zip',  # 修正MIME类型为ZIP
        type='primary',
        use_container_width=True
    )

with col_C:
    # 创建下载按钮
    st.download_button(
        label='下载"学科"成绩表',
        data=zp_sub,
        file_name="学科成绩表.zip",
        mime='application/zip',  # 修正MIME类型为ZIP
        type='primary',
        use_container_width=True
    )


st.write("***")
st.markdown("### 🚩:red[合并成绩表]")


