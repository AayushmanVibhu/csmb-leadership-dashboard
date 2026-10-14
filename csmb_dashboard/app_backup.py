from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='CSMB | Leadership Overview',page_icon='📊',layout='wide')
st.markdown('''<style>
.block-container{padding-top:1.4rem;max-width:1400px}
h1,h2,h3{color:#102A56}
[data-testid="stMetric"]{background:#f2f6fc;border:1px solid #dce6f2;padding:16px 20px;border-radius:12px}
[data-testid="stMetricLabel"]{color:#355579}
</style>''',unsafe_allow_html=True)
DATA=Path(__file__).parent/'data'
companies=pd.read_csv(DATA/'companies.csv')
engagements=pd.read_csv(DATA/'engagements.csv',parse_dates=['date'])
projects=pd.read_csv(DATA/'projects.csv')
attention=pd.read_csv(DATA/'attention.csv')

st.title('CSMB | Leadership Overview')
st.caption('Dashboard prototype • Fictional hiring-exercise dataset • Not actual CSMB records')
choice=st.selectbox('Company filter',['All Companies']+sorted(companies.company.tolist()))
if choice=='All Companies':
    ids=set(companies.company_id)
else:
    ids=set(companies.loc[companies.company==choice,'company_id'])
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
m4.metric('Projects completed',f'{completed} / {len(p)}',help=f'{completion:.1f}% of projects are marked Completed; this is not verified business impact')

left,right=st.columns([1.3,1])
with left:
    st.subheader('Project pipeline')
    order=['Completed','In Progress','Not Started']
    counts=p.status.value_counts().reindex(order,fill_value=0).reset_index()
    counts.columns=['Status','Projects']
    fig=px.bar(counts,x='Projects',y='Status',orientation='h',text='Projects',color='Status',color_discrete_map={'Completed':'#087F8C','In Progress':'#2878C8','Not Started':'#E6A23C'},category_orders={'Status':order})
    fig.update_layout(showlegend=False,margin=dict(l=10,r=20,t=10,b=10),height=265,xaxis_title='',yaxis_title='',paper_bgcolor='white',plot_bgcolor='white')
    fig.update_yaxes(autorange='reversed')
    fig.update_xaxes(dtick=1,showgrid=True,gridcolor='#edf1f6')
    st.plotly_chart(fig,use_container_width=True)
with right:
    st.subheader('Engagement mix')
    ec=e.type.value_counts().rename_axis('Type').reset_index(name='Engagements')
    fig2=px.pie(ec,values='Engagements',names='Type',hole=.65,color='Type',color_discrete_map={'SMB Lab':'#2878C8','Follow-up':'#13A89E'})
    fig2.update_layout(height=265,margin=dict(l=10,r=10,t=10,b=10),legend=dict(orientation='h',y=-.05,x=.1))
    st.plotly_chart(fig2,use_container_width=True)

st.subheader(f'Action required  ·  {len(a)} flagged businesses')
if len(a):
    st.dataframe(a[['company','category','issue','recommended_action']].rename(columns={'company':'Business','category':'Category','issue':'Evidence from sample','recommended_action':'Suggested next step'}),hide_index=True,use_container_width=True)
else: st.info('No attention items recorded for this selection.')
st.caption('Interpretation: Project status and founder-reported improvements are not equivalent to independently verified business outcomes. Follow-up flags indicate missing records in this sample, not proof that follow-up did not occur.')
with st.expander('Evidence and methodology'):
    st.write('All counts are calculated from the CSV tables supplied with this prototype. Repeat engagement rate = companies with more than one engagement ÷ companies in the selected view. Project completion = projects marked Completed ÷ projects in view.')
    st.write('The fictional source uses inconsistent industry/location labels; companies are matched by stable IDs. Confidential staff-only information is intentionally excluded from this leadership demonstration.')
    st.dataframe(a[['company','evidence']] if len(a) else pd.DataFrame(),hide_index=True,use_container_width=True)
