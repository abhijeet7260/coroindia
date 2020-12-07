from flask import *
import requests
from flask_table import Table, Col, LinkCol
import heapq
import pandas as pd
import plotly
import plotly.express as px

app = Flask(__name__)

response = requests.get("https://api.rootnet.in/covid19-in/stats/latest")
data=response.json()
india_offical=data['data']['summary'] #india offical data
states=list()
total_cases=list()
active_cases=list()
recovered_cases=list()
death_cases=list()
state_wise_data=list(data['data']['regional'])
for i in state_wise_data:
    states.append(str(i['loc']))
    total_cases.append(int(i['totalConfirmed']))
    active_cases.append(int(i['totalConfirmed'])-int(i['discharged'])-int(i['deaths']))
    recovered_cases.append(int(i['discharged']))
    death_cases.append(int(i['deaths']))

df=pd.DataFrame({'State':states,'Active Cases':active_cases})
fig = px.choropleth(
    df,
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
    featureidkey='properties.ST_NM',
    locations='State',
    color='Active Cases',
    color_continuous_scale='Reds'
)

fig.update_geos(fitbounds="locations", visible=False)
plotly.io.to_html(fig, include_plotlyjs=False, full_html=True)
lol=plotly.io.to_html(fig,full_html=False,default_width="100%",default_height="100%")

class SortableTable(Table):
    states1 = Col('States')
    total_cases1 = Col('Total Cases')
    active_cases1 = Col('Active')
    recovered_cases1 = Col('Recovered')
    death_cases1 = Col('Deceased')
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('index', sort=col_key, direction=direction)

@app.route('/')
def index():
    sort = request.args.get('sort', 'states1')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    table = SortableTable(Item.get_sorted_by(sort, reverse),
                          sort_by=sort,
                          sort_reverse=reverse,
                          table_id='table_india')
    return render_template('root.html', tStrToLoad=table.__html__(),lol=lol)

class Item(object):
    """ a little fake database """
    def __init__(self, states1,total_cases1,active_cases1,recovered_cases1,death_cases1):
        self.states1 = states1
        self.total_cases1 = total_cases1
        self.active_cases1 = active_cases1
        self.recovered_cases1 =recovered_cases1
        self.death_cases1=death_cases1

    @classmethod
    def get_elements(cls):
        temp=list()
        for i,j,k,l,m in zip(states,total_cases,active_cases,recovered_cases,death_cases):
            temp.append(Item(i,j,k,l,m))
        return temp
    @classmethod
    def get_sorted_by(cls, sort, reverse=False):
        return sorted(
            cls.get_elements(),
            key=lambda x: getattr(x, sort),
            reverse=reverse)

    @classmethod
    def get_element_by_id(cls, states1):
        return [i for i in cls.get_elements() if i.states1 == states1][0]


if __name__ == '__main__':
    app.run(debug=True)
