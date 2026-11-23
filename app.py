import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_calendar import calendar


st.title('ToDo リスト')
st.subheader('タスク一覧')



jst = ZoneInfo("Asia/Tokyo")
today=datetime.now(tz=jst).date()
jpn_dt=pd.Timestamp(today)

sample_rows=[
    # (名前, 状態, 今日から何日後か)
    ("数学のレポート提出", "完了", -9),
    ("英語の単語テスト勉強", "完了", -7),
    ("実験レポートを書く", "未完了", -5),
    ("図書館の本を返却", "未完了", -3),
    ("Python課題を提出", "未完了", 0),
    ("バイトのシフト提出", "完了", -1),
    ("ゼミの相談メール", "未完了", 2),
    ("部屋の掃除", "未完了", 5),
    ("資格試験の申し込み", "未完了", 10),
    ("友人へのプレゼント購入", "完了", -6),
    ("ゼミ発表の資料作成", "未完了", 14),
    ("帰省チケットの予約", "未完了", 21),
]

sample_df=pd.DataFrame(
    data=sample_rows,
    columns=["name", "status", "days"],
)

sample_df['deadline']=(jpn_dt+pd.to_timedelta(sample_df['days'],unit='D')).dt.strftime('%Y-%m-%d')

sample_df.insert(0, "id", range(1, len(sample_df) + 1))
sample_csv=(
    sample_df[["id", "name", "status", "deadline"]]
    .to_csv(index=False)
    .encode("utf-8-sig")
)

st.download_button(
    label='sample csvのダウンロード',
    data=sample_csv,
    file_name='sample_csv.csv',
    mime="text/csv",
)

uploaded_file=st.file_uploader("CSVを選んでください", type="csv", accept_multiple_files=False)

if uploaded_file :
    try:
        
        df=pd.read_csv(uploaded_file,encoding='utf-8')

    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df=pd.read_csv(uploaded_file,encoding='cp932')


    columns_judge=set(['name','status','deadline']).issubset(df.columns)
    if columns_judge is False:
        st.error('必要な列:"name" "status" "deadline"')
        st.stop()

    all_tasks_length=len(df['name'])
    status_count=df['status'].value_counts()
    complete=status_count.get('完了',0)
    incomplete=status_count.get('未完了',0)

    if all_tasks_length==0:
        completion_rate='タスクがありません'
        rate_text=completion_rate
    else:
        completion_rate=round((complete/all_tasks_length)*100,1)
        rate_text=f'{completion_rate}%'

    
    col1, col2, col3 = st.columns(3)
    with col1:     
        st.metric("総数", all_tasks_length)

    with col2:
        st.metric(
            label="完了率",
            value=rate_text
        )

    with col3:
        st.metric(
            label='未完了のタスク',
            value=f'{incomplete}個'
        )

   
    df['deadline']=pd.to_datetime(df['deadline'],errors='coerce')

    overdue_df=df[(df['deadline']<jpn_dt)&(df['status']=='未完了')]
    overdue_incomplete_num=len(overdue_df)

    col1,col2=st.columns([2,1])
    with col1:
        st.subheader('未完了で期限切れのタスク一覧')
        

    with col2:
        if overdue_incomplete_num>0:
            st.error(f'{overdue_incomplete_num}件')


        else:
            st.success('タスクは存在しません')

    
    st.subheader('未完了と完了件数')
    st.bar_chart(status_count)

   
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(':blue[blue=未完了]')
    with col2:
        st.markdown(':green[green=完了済み]')

    with col3:
        st.markdown(':red[red=期限切れ]')

    #calender
    events=[]
    for id_,row in df.iterrows():
        
        task_name=row['name']
        if not pd.isna(row['deadline']):
            deadline=row['deadline'].strftime('%Y-%m-%d')

            if (row['deadline']<jpn_dt)&(row['status']=='未完了'):
                color='#FF0000'

            elif row['status']=='完了':
                color='#3BB143'

            else:
                color='#0000FF'

            events.append({
                "title":task_name,
                "start": deadline,
                "end": deadline,
                "backgroundColor": color,
            })
        
    calendar_options={
        'locale':'ja',
        "initialView": "dayGridMonth",
        'editable':False,
    }

    calendar(events=events, options=calendar_options)

    #フィルターの作成
    selected_filter=st.selectbox(
        'ToDoリストの抽出',
        ("すべて", "未完了のみ", "期限切れのみ"),
    )

    if selected_filter=='すべて':
        selected_df=df
    elif selected_filter=='未完了のみ':
        selected_df=df[df['status']=='未完了']
    elif selected_filter=='期限切れのみ':
        selected_df=df[(df['deadline']<jpn_dt)&(df['status']=='未完了')]

    st.dataframe(
        selected_df,
        column_config={
            "deadline": st.column_config.DateColumn("deadline", format="YYYY-MM-DD")
            }
            )

    search_word=st.text_input(
     label='検索したいワードを入力',
     value=None,   
    )

    search_word = search_word or ""
    searched_word=df['name'].str.contains(
        pat=search_word,
        case=False,
        na=False,
        regex=False,
    )
    if search_word:
        searched_word_df = df[searched_word]
        st.dataframe(
            searched_word_df,
            column_config={
                "deadline": st.column_config.DateColumn("deadline", format="YYYY-MM-DD")
            },
        )

    search_word=st.text_input(
     label='締め切りの日時を入力',
     value=None, 
     placeholder='例: 2026-11-23',  
    )

    search_deadline = search_word or ""
    deadline_txt=df['deadline'].dt.strftime('%Y-%m-%d')
    
    searched_deadline=deadline_txt.str.contains(
        pat=search_deadline,
        case=False,
        na=False,
        regex=False,
    )

    if search_deadline:
        searched_deadline_df = df[searched_deadline]
        st.dataframe(
            searched_deadline_df,
            column_config={
                "deadline": st.column_config.DateColumn("deadline", format="YYYY-MM-DD")
            },
        )

