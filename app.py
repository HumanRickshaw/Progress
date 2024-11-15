#######Packages######
from dash import callback, ctx, Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate as PU
from datetime import date
from datetime import datetime as dt
import pandas as pd
from pandas.api.types import CategoricalDtype as CDT
import plotly.express as px
#######End Packages######





######Helper Functions######

def create_hlink(text, link, center = False) :

    style = {'fontSize': 18}
    if center :
        style['textAlign'] ='center'

    return(dbc.Row([html.A(text, href = link, target = '_blank', style = style)]))



def filterDF(df, lref, fill) :
    '''
    Update the df to graph fill type and type of link.
    '''
    if fill == 'Political Party' :
        #Use Status and Party to create categories for fill.
        def createGroup(row) :
            if row['Status'] == 'Yes' :
                if row['Party'] == 'Democrat':
                    return 'Democrat - Passed'
                else :
                    return 'Republican - Passed'
            elif row['Status'] == 'Partial' : 
                if row['Party'] == 'Democrat':
                    return 'Democrat - Partial'
                else :
                    return 'Republican - Partial'
            elif row['Status'] == 'Deferred':
                return 'Motion Deferred'

        df['Group'] = df.apply(createGroup, axis=1)
        df['Group'] = pd.Categorical(df['Group'],
                                     categories = ['Democrat - Passed',
                                                   'Republican - Passed',
                                                   'Democrat - Partial',
                                                   'Republican - Partial',
                                                   'Motion Deferred'],
                                     ordered = True)
        df = df[df['Type'] == lref][['State', 'Abbr', 'Date', 'Status', 'Party', 'Title', 'Link', 'Group']]
        df.sort_values(by = ['Group'], inplace = True)
    
    else :
        df = df[df['Type'] == lref][['State', 'Abbr', 'Date', 'Status', 'Party', 'Title', 'Link', 'NumericData']]
   
    df['Title2'] = df['Title'].apply(lambda x: '<No ' + lref + ' Found>' if x == ' ' else x[0:50] + '...')
    return(df)
######End Helper Functions######





######Constants######

#Get today's date for States for cumulative.
tod = date.today()
today = tod.strftime('%B') + ' ' + str(tod.day) + ', ' + str(tod.year)

#Map FIPS
fips_source = 'https://raw.githubusercontent.com/kjhealy/us-county/master/data/census/fips-by-state.csv'

#About.
about_the_app = [dbc.Row('I often question how societies and humanity progress.  What was that like hundreds of years ago?  What will that look like hundreds of years from now?'),
                 html.Br(),
                 dbc.Row('There has been much progress in the US in the past couple hundred years, but the past decade or two, as well as the next four years,will have been concerning for many.'),  
                 html.Br(),
                 dbc.Row('In any trend in society or nature, it is almost never a perfectly increasing or decreasing line or curve.  Yes, overall a pattern can emerge and causality understood, but it is to be expected that instances of the opposite will occur...on the regular.  In these moments, I find it comforting totake a step back, and remember our time is part of the history for the future.'),
                 html.Br(),
                 dbc.Row('One way to do this, is to seek out progress happening somewhat less in the spotlight.  And because it is bipartisan, it happens fairly smoothly and quickly.'),
                 html.Br(),
                 dbc.Row('I took it upon myself to dig deep, acquire dates, government documents, news articles, political information, population numbers...and make a map.  Makinginteractive, choropleth mapsis one of my favorite analysis and visualization tasks.  One has the opportunity to create a puzzle, piece by piece, without knowing the final picture. Simply let the story unfold.'),
                 html.Br(),
                 dbc.Row('Some information of relevance:'),
                 dbc.Row('* If the state is shaded, it will have at least one of the three links.  Some states have far more active posting on their goverment websites, as well as news reporting.'),
                 dbc.Row('* For simplicity, the color of the state is shaded by Political Party of the Governor, who often, but not always, signed the Executive Order or Legislative Bill.'),
                 dbc.Row('* Partial means some conversations have been had, perhaps a proposal, or even a passed bill for a subset of the population or jobs. Check out the Links.'),
                 dbc.Row('* This will eventually be part of a much, much larger exploration.'),
                 html.Br(),                 
                 dbc.Row('Enjoy! - Rohan')]

#Links.
links_title = [create_hlink('Best Colleges :',
                            'https://www.bestcolleges.com/news/these-states-dont-require-degree-for-a-government-job/'),
               create_hlink('CBS :',
                            'https://www.cbsnews.com/news/jobs-college-degree-requirement/'),
               create_hlink('National Conference of State Legislatures :',
                            'https://www.ncsl.org/education/states-consider-elimination-of-degree-requirements'),
               create_hlink('National Govenor’s Association :',
                            'https://www.nga.org/news/commentary/governors-leading-on-skills-based-hiring-to-open-opportunity-pathways/'),
               create_hlink('New York Times :',
                            'https://archive.is/H39Kz')]

links_href = [create_hlink('These States Don’t Require a Degree for a Government Job',
                           'https://www.bestcolleges.com/news/these-states-dont-require-degree-for-a-government-job/'),  
              create_hlink('1 in 3 companies have dropped college degree requirements for some jobs.',
                           'https://www.cbsnews.com/news/jobs-college-degree-requirement/'), 
              create_hlink('States Consider Elimination of Degree Requirements',
                           'https://www.ncsl.org/education/states-consider-elimination-of-degree-requirements'), 
              create_hlink('Governors Leading on Skills-Based Hiring to Open Opportunity Pathways',
                           'https://www.nga.org/news/commentary/governors-leading-on-skills-based-hiring-to-open-opportunity-pathways/'), 
              create_hlink('A 4-Year Degree Isn’t Quite the Job Requirement It Used to Be',
                           'https://archive.is/H39Kz')]                          

#Last Modified.
last_modified = 'This page was last modified by Rohan Lewis on ' + today + ' at ' + str(dt.now().time())[0:8] + '.'

#GitHubRepository
git_repo = create_hlink('Git Hub Respository',
                        'https://github.com/HumanRickshaw/Progress')

#Fill options.
fill1 = ['Political Party',
         'Date of Legislation']

fill2 = ['Complete Legislation',
         'Complete & Partial']

media = ['State Gov. Website/Press Release',
         'Executive Order/Legislation',
         'Media/Other News']

#Colors
bold = ['#0057CE', '#B82100', '#AAC7EE', '#E7B5AA', '#303030']
######End Constants######






######DF######

#Read.
dfs = pd.read_csv('data.csv', encoding = 'Latin-1')

#Date Format.
dfs['Date'] = pd.to_datetime(dfs['Date'], format= '%Y-%m-%d')

#Date Range.
mind = min(dfs.Date)
maxd = max(dfs.Date)
max_val = (maxd-mind).days

dfs['NumericData'] = dfs['Date']
dfs.NumericData = dfs.NumericData.apply(lambda x: (x - mind).days)

label0 = mind.strftime('%b %Y')
label1 = (mind + pd.Timedelta(days = max_val/3)).strftime('%b %Y')
label2 = (maxd - pd.Timedelta(days = max_val/3)).strftime('%b %Y')
label3 = maxd.strftime('%b %Y')

marks = {0 : {'label' : label0,
              'style' : {'margin-right' : 0,
                         'width': '100px'}},
         max_val : {'label' : label3,
                    'style' : {'margin-left' : 0,
                               'width': '100px'}}}
######DF######





######Initialize the App######
# name your app 'app'
app = Dash(__name__)
# add this line below
server = app.server
app.config.external_stylesheets = [dbc.themes.GRID]
app.config.suppress_callback_exceptions = True

#App layout
app.layout = dbc.Container([#Title
                            dbc.Row([dbc.Col(html.H1('Removing Degree Requirements for State Jobs',
                                                     style = {'textAlign' : 'center'}),
                                                     width = 11)]),
                                                       
                            #Show/Hide About.
                            dbc.Row([dbc.Col(width = 5),
                                     dbc.Col([html.Button('About',
                                                           id = 'aboutb',
                                                           style = {'fontSize': 16,
                                                                    'textAlign': 'center'},
                                                           n_clicks = 0)],
                                             width = 1),
                                     dbc.Col(width = 5)]),
                            
                            dbc.Row([html.Br()]),
                            
                            dbc.Row([dbc.Col(width = 2),
                                     dbc.Col(id = 'aboutt',
                                             children = about_the_app,
                                             style = {'fontSize': 18,
                                                      'display': 'none'}),
                                    dbc.Col(width = 3)]),
                          
                           
                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            
                            #######Interactive Row######
                            dbc.Row([dbc.Col(width = 2),
                                    
                                     dbc.Col([html.Div('Select External Links :',
                                                       style = {'fontSize': 18,
                                                                'textAlign' : 'right'})],
                                             width = 2),
                                    
                                     dbc.Col([dcc.RadioItems(id = 'linkref',
                                                             options = media,
                                                             value = media[0],
                                                             style = {'fontSize': 18,
                                                                      #'margin-left' : 'auto',
                                                                      #'margin-right' : 0
                                                                      })],
                                             width = 2),

                                     dbc.Col([html.Div('Fill By:',
                                                       style = {'fontSize': 18,
                                                                'textAlign' : 'right'})],
                                             width = 1),

                                     dbc.Col([dcc.RadioItems(id = 'fill_by1',
                                                             options = fill1,
                                                             value = fill1[0],
                                                             style = {'fontSize': 18})],
                                             width = 2),

                                     dbc.Col(width = 3)]),
                            #######End Interactive Row######

                            #######Conditional Row######
                            dbc.Row([dbc.Col(width = 7),
                                     
                                     dbc.Col([dcc.RadioItems(id = 'fill_by2',
                                                             options = [],
                                                             value = None,
                                                             style = {'fontSize': 18})],
                                             width = 2),
                                    
                                    dbc.Col(width = 5)]),
                            #######End Conditional Row######

                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            
                            #External Link.
                            dbc.Row([dbc.Col(width = 2),
                                     dbc.Col(html.Div(id = 'click_link',
                                                       style = {'textAlign': 'center'}),
                                             width = 7)]),
 
                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            
                            #USA Map.
                            dbc.Row([dbc.Col(width = 2),
                                     dbc.Col([dcc.Graph(id = 'graph1')], width = 8),
                                     dbc.Col(width = 2)]),
                            
                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            
                            #Show/Hide Additional Links.
                            dbc.Row([dbc.Col(width = 5),
                                     dbc.Col([html.Button('Additional Links',
                                                           id = 'addlinkb',
                                                           style = {'fontSize': 16,
                                                                    'textAlign': 'center'},
                                                           n_clicks = 0)],
                                             width = 2),
                                     dbc.Col(width = 5)]),

                            dbc.Row([html.Br()]),
                            
                            dbc.Row([dbc.Col(width = 2),

                                     dbc.Col(id = 'addlinkt',
                                             children = [dbc.Row([dbc.Col(links_title,
                                                                          style = {'fontSize': 18,
                                                                                   'textAlign': 'right'},
                                                                          width = 3),
                                              
                                                                  dbc.Col(links_href,
                                                                          style = {'fontSize': 18,
                                                                                   'textAlign': 'left'},
                                                                          width = 5)])],
                                             style = {'fontSize': 18,
                                                      'display': 'none'})]),

                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),
                            dbc.Row([html.Br()]),

                            #Last Modified.                            
                            dbc.Row([html.Div(last_modified,
                                              style = {'fontSize': 18})]),

                            dbc.Row([html.Br()]),

                            #GitHub Repository.
                            git_repo],
                            fluid = True)    





#About - Top Center.
@callback(Output('aboutt', 'style'),
          Input('aboutb', 'n_clicks'))
def show(clicks) :
    if clicks % 2 == 1 :
        return {'display': 'block'}
    else :
        return {'display': 'none'}





#Additional Links - Bottom Center.
@callback(Output('addlinkt', 'style'),
          Input('addlinkb', 'n_clicks'))
def show(clicks) :
    if clicks % 2 == 1 :
        return {'display': 'block'}
    else :
        return {'display': 'none'}





#Conditional Fill for Date of Legislation.
@callback(Output('fill_by2', 'options'),
          Output('fill_by2', 'value'),
          Input('fill_by1', 'value'))
def insert(fill1) :
    if fill1 == 'Date of Legislation' :
        return(fill2, fill2[0])
    else :    
        return([], None)





#Choropleth
@callback(Output('graph1', 'figure'),
          Output('click_link', 'children'),
          Input('linkref', 'value'),
          Input('fill_by1', 'value'),
          Input('fill_by2', 'value'),
          Input('graph1', 'clickData'))
def updateOutput(lref, fill1, fill2, clickData):

    print(lref)
    print(fill)    
 
    #Drill down by date and link.
    dff = filterDF(dfs, lref, fill1)

    if fill1 == 'Political Party' :
       
        fig = px.choropleth(data_frame = dff,
                            locations = 'Abbr',
                            locationmode = 'USA-states',
                            color = 'Group',
                            color_discrete_sequence = bold,
                            hover_name = 'Title2',
                            hover_data = {'Group' : False,
                                          'Abbr' : False},
                            custom_data = ['Title', 'Link'])

        fig.update_layout(title = None,
                          legend = {'entrywidth' : 0.33,
                                    'entrywidthmode' : 'fraction',
                                    'title' : '<b>Degree Requirements <br>          Eliminated</b>',
                                    'font' : {'size' : 20}, 
                                    'orientation': 'v',
                                    'x' : 0.9,
                                    'y' : 0.5,
                                    'xanchor' : 'left',
                                    'yanchor' : 'middle'},
                          geo_scope = 'usa',
                          margin = {'l' : 0, 't' : 0, 'r' : 0, 'b' : 0}) 

    else :
        dff = filterDF(dfs, lref, fill1)
        if fill2 == 'Complete Legislation' :
            dff = dff[dff['Status'] == 'Yes']
        else :
            dff = dff[dff['Status'] != 'Deferred']

        fig = px.choropleth(data_frame = dff,
                            locations = 'Abbr',
                            locationmode = 'USA-states',
                            color = 'NumericData',
                            color_continuous_scale = 'Viridis_r',
                            hover_name = 'Title2',
                            hover_data = {'NumericData' : False,
                                          'Abbr' : False},
                            custom_data = ['Title', 'Link'])

        fig.update_layout(geo_scope = 'usa',
                          margin = {'r' : 0, 't' : 0, 'l' : 0, 'b' : 0})
        
        fig.update_coloraxes(colorbar_title_text = 'Date of <br> Action',
                             colorbar_title_font_size = 20,
                             colorbar_xpad = 20,
                             colorbar_thickness = 75,
                             colorbar_tickfont_size = 16,
                             colorbar_tickvals = [0, max_val/3, 2*max_val/3, max_val],
                             colorbar_ticktext = [label0, label1, label2, label3])

    #Create URL if the map gets clicked.
    url = ''
    if ctx.triggered_id == 'graph1' :
 
         url = create_hlink(clickData['points'][0]['customdata'][0],
                            clickData['points'][0]['customdata'][1],
                            True)
    return(fig, url)

# Run the app.
if __name__ == '__main__':
    app.run(debug = True)



#https://www.brookings.edu/articles/states-are-leading-the-effort-to-remove-degree-requirements-from-government-jobs/
#https://www.prnewswire.com/news-releases/five-states-join-ambitious-nationwide-effort-to-tear-the-paper-ceiling-and-accelerate-opportunity-for-workers-skilled-through-alternative-routes-stars-302289508.html
