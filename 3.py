import streamlit as st
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns

dir_ = r"C:\\obj2\\ad\\lab2\\lab_2"

def remove_tags(text):
    return re.sub(r'<.*?>', '', str(text))

def frame(dir_):
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    csv_files = [file for file in os.listdir(dir_) if file.endswith('.csv')]
    data = []
    for file_name in csv_files:
        file_path = os.path.join(dir_, file_name)
        part = file_name.split('_')
        prov_ID = int(part[1]) if len(part) > 1 and part[1].isdigit() else None
        df = pd.read_csv(file_path, header=1, names=headers)
        df = df.iloc[:-1]
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df['Year'] = df['Year'].apply(remove_tags)
        df = df.drop(columns=['empty'])
        df['province_id'] = prov_ID
        data.append(df)

    if not data:
        return pd.DataFrame(columns=headers[:-1] + ['province_id'])

    result = pd.concat(data).drop_duplicates().reset_index(drop=True)
    result['Year'] = pd.to_numeric(result['Year'], errors='coerce').astype('Int64')
    result["VCI"] = pd.to_numeric(result["VCI"], errors='coerce')
    result["TCI"] = pd.to_numeric(result["TCI"], errors='coerce')
    result["VHI"] = pd.to_numeric(result["VHI"], errors='coerce')
    result = result.sort_values(by=['province_id', 'Year', 'Week']).reset_index(drop=True)
    return result

df = frame(dir_)

def reset_filt():
    st.session_state.clear()
    st.session_state['indicator'] = 'VCI'
    st.session_state['selected_province'] = df['province_id'].unique()[0] if not df.empty else None
    st.session_state['week_range'] = (1, 52)
    st.session_state['year_range'] = (1997, 2025)
    st.session_state['sort_asc'] = False
    st.session_state['sort_desc'] = False
    st.rerun()

if 'indicator' not in st.session_state:
    st.session_state['indicator'] = 'VCI'
    st.session_state['selected_province'] = df['province_id'].unique()[0] if not df.empty else None
    st.session_state['week_range'] = (1, 52)
    st.session_state['year_range'] = (1997, 2025)
    st.session_state['sort_asc'] = False
    st.session_state['sort_desc'] = False

tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння"])

col1, col2 = st.columns([1, 2])
with col1:
    st.header("Фільтри")
    indicator = st.selectbox("Оберіть показник", ["VCI", "TCI", "VHI"], key='indicator')

    area_names = {int(id): f"Область {id}" for id in df['province_id'].unique()}
    selected_area = st.selectbox("Оберіть область", list(area_names.values()))
    selected_province = int([k for k, v in area_names.items() if v == selected_area][0])
    st.session_state['selected_province'] = selected_province

    week_range = st.slider("Виберіть інтервал тижнів", 1, 52, key='week_range')
    year_range = st.slider("Виберіть інтервал років", 1997, 2025, key='year_range')

    sort_asc = st.checkbox("Сортувати за зростанням", key="sort_asc")
    sort_desc = st.checkbox("Сортувати за спаданням", key="sort_desc")

    if sort_asc and sort_desc:
        st.warning("Не можна одночасно обрати сортування за зростанням і спаданням!")
    if st.button("Скинути фільтри"):
        reset_filt()

with col2:
    filtered_data = df[(df['Year'].between(*st.session_state['year_range'])) &
                       (df['Week'].between(*st.session_state['week_range'])) &
                       (df['province_id'] == st.session_state['selected_province'])]
    if sort_asc and not sort_desc:
        filtered_data = filtered_data.sort_values(by=st.session_state['indicator'], ascending=True)
    elif sort_desc and not sort_asc:
        filtered_data = filtered_data.sort_values(by=st.session_state['indicator'], ascending=False)
    elif sort_asc and sort_desc:
        st.warning("Сортування не буде застосовано: обрані обидва типи сортування.")

    with tab1:
        st.write("Таблиця з відфільтрованими даними")
        st.dataframe(filtered_data[["Year", "Week", st.session_state['indicator'], "province_id"]].head(100))

    with tab2:
        st.write(f"Графік {st.session_state['indicator']} для області {st.session_state['selected_province']}")
        if not filtered_data.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(x='Week', y=st.session_state['indicator'], data=filtered_data.astype({'Year': 'int'}),
                         hue='Year', ax=ax)
            ax.set_xlabel("Тиждень")
            ax.set_ylabel(st.session_state['indicator'])
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("Немає даних для відображення графіка.")

    with tab3:
        st.write(f"Порівняння {st.session_state['indicator']} для обраної області")
        comparison_data = df[(df['Year'].between(*st.session_state['year_range'])) &
                             (df['Week'].between(*st.session_state['week_range'])) &
                             (df['province_id'] == st.session_state['selected_province'])]
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='Week', y=st.session_state['indicator'], data=comparison_data,
                     hue='province_id', ax=ax)
        ax.set_xlabel("Тиждень")
        ax.set_ylabel(st.session_state['indicator'])
        st.pyplot(fig)
        plt.close(fig)
