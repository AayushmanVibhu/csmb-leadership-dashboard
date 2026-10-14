from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="CSMB | Leadership Overview", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
.stApp, [data-testid="stAppViewContainer"] {background:#ffffff;color:#102A56}
.block-container {padding-top:0.8rem;padding-bottom:0.5rem;max-width:1400px}
h1 {font-size:2.15rem!important;margin-bottom:0!important;color:#102A56!important}
h2,h3 {color:#102A56!important}
[data-testid="stMetric"] {background:#F0F5FB;border:1px solid #D9E4F2;padding:13px 17px;border-radius:11px}
[data-testid="stMetricValue"] {color:#102A56!important;font-size:2rem!important}
[data-testid="stMetricLabel"] p {color:#355579!important;font-weight:600!important}
[data-testid="stCaptionContainer"] p {color:#52647C!important}
[data-testid="stSelectbox"] label p {color:#102A56!important;font-weight:600}
[data-testid="stDataFrame"] {border:1px solid #D9E4F2;border-radius:8px}
[data-testid="stVerticalBlock"] {gap:0.55rem}
[data-testid="stHeader"] {
    display: none !important;
}

.block-container {
    padding-top: 1.5rem !important;
}
</style>""", unsafe_allow_html=True)

DATA=Path(__file__).parent/'data'
companies=pd.read_csv(DATA/'companies.csv')
engagements=pd.read_csv(DATA/'engagements.csv',parse_dates=['date'])
projects=pd.read_csv(DATA/'projects.csv')
attention=pd.read_csv(DATA/'attention.csv')

st.title('CSMB | Leadership Overview')
st.caption('Interactive prototype  •  Fictional hiring-exercise data  •  Not actual CSMB records')
choice=st.selectbox('Company filter',['All Companies']+sorted(companies.company.tolist()))
ids=set(companies.company_id) if choice=='All Companies' else set(companies.loc[companies.company==choice,'company_id'])
c=companies[companies.company_id.isin(ids)]
e=engagements[engagements.company_id.isin(ids)]
p=projects[projects.company_id.isin(ids)]
a=attention[attention.company_id.isin(ids)].merge(companies[['company_id','company']],on='company_id')
repeated=int((e.groupby('company_id').size()>1).sum())
completed=int((p.status=='Completed').sum())
rate=100*repeated/len(c) if len(c) else 0
completion=100*completed/len(p) if len(p) else 0
m1,m2,m3,m4=st.columns(4)
m1.metric('Businesses served',len(c))
m2.metric('Total engagements',len(e))
m3.metric('Repeat engagement rate',f'{rate:.1f}%',help=f'{repeated} of {len(c)} companies have more than one recorded engagement')
m4.metric('Projects completed',f'{completed} / {len(p)}',help=f'{completion:.1f}% marked completed, not verified impact')

left,right=st.columns([1.2,1])
with left:
    st.subheader('Project pipeline')
    order=['Completed','In Progress','Not Started']
    counts=p.status.value_counts().reindex(order,fill_value=0).reset_index()
    counts.columns=['Status','Projects']
    fig=px.bar(counts,x='Projects',y='Status',orientation='h',text='Projects',color='Status',color_discrete_map={'Completed':'#087F8C','In Progress':'#2878C8','Not Started':'#E6A23C'},category_orders={'Status':order})
    fig.update_layout(showlegend=False,height=225,margin=dict(l=4,r=20,t=3,b=5),font=dict(color='#102A56',size=13),paper_bgcolor='white',plot_bgcolor='white',xaxis_title='',yaxis_title='')
    fig.update_yaxes(autorange='reversed',tickfont=dict(color='#102A56',size=12))
    fig.update_xaxes(dtick=1,showgrid=True,gridcolor='#E8EEF5',tickfont=dict(color='#52647C'))
    fig.update_traces(textposition='inside',textfont=dict(color='white',size=13))
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
with right:
    st.subheader('Engagement mix')
    ec=e.type.value_counts().rename_axis('Type').reset_index(name='Engagements')
    fig2=px.pie(ec,values='Engagements',names='Type',hole=.64,color='Type',color_discrete_map={'SMB Lab':'#2878C8','Follow-up':'#13A89E'})
    fig2.update_layout(height=225,margin=dict(l=5,r=5,t=0,b=5),font=dict(color='#102A56',size=13),paper_bgcolor='white',legend=dict(orientation='h',y=-.08,x=.17,font=dict(color='#102A56')))
    fig2.update_traces(textfont=dict(color='white',size=13))
    st.plotly_chart(fig2,use_container_width=True,config={'displayModeBar':False})

st.subheader(f'Action required  ·  {len(a)} flagged businesses')
if len(a):
    st.dataframe(a[['company','category','issue','recommended_action']].rename(columns={'company':'Business','category':'Category','issue':'Evidence from sample','recommended_action':'Suggested next step'}),hide_index=True,use_container_width=True,height=185)
else:
    st.info('No attention items recorded for this selection.')
st.caption('Methodology: Completion ≠ verified business impact. Missing follow-up records in this sample do not prove no follow-up occurred.')
with st.expander('Evidence and methodology'):
    st.write('All counts are computed from the included CSV files. Repeat engagement rate = businesses with >1 recorded engagement / businesses in selected view.')
    st.write('Company identifiers standardize inconsistent industry/location labels. Private staff-only information is excluded from this demonstration.')
    if len(a): st.dataframe(a[['company','evidence']],hide_index=True,use_container_width=True)
