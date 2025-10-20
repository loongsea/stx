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

st.markdown("### 🚩:red[合并成绩表]")
st.write("***")
# 创建一个上传多个文件的按钮
up_mfile = st.file_uploader("上传年级成绩总表", type=["xlsx"],accept_multiple_files=True)

# 读取工作薄为一个df对象
if not up_mfile:
    st.text_area(label='设置说明', value="将《班级成绩表》、《班级_学科成绩表》、《学科成绩表》，合并为一个《级段成绩总表》", height=80)
    exit()
elif up_mfile:
    # 将up_mfile中的多个文件分别读取为一个df对象
    dfs_dic = {file.name: pd.read_excel(file, engine='openpyxl') for file in up_mfile}

# 合并多个df对象为一个df对象
dfs_all = al.merge_multiple_dfs(dfs_dic.values(), on=['学号'], how='outer', keep_last=True)

genre = st.radio(label='参照列',options=('依据《学号》列汇总', '依据《姓名》列汇总'),index=0, horizontal=True,label_visibility="collapsed")
match genre:
    case '依据《学号》列汇总':
        rdo='学号'
    case '依据《姓名》列汇总':
        rdo='姓名'
    case _:
        st.write('请选择.')

# 对列索引排序，并按学号对行数据排序
dfs_all = al.df_sort(dfs_all, cols=['班级', '学号','姓名','语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理'],idx=rdo)

if st.checkbox(label='显示全部',value= False):
    st.dataframe(dfs_all,use_container_width= True)
else:
    st.dataframe(dfs_all.head(2), use_container_width=True)

down = al.df_to_bytesIO(dfs_all)
st.download_button(label="下载合并后的工作表",
                   data=down,
                   file_name="合并后的工作表.xlsx",
                   use_container_width=True,
                   type="primary",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")