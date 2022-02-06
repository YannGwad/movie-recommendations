
# IMPORTS
import pandas as pd
from dash import Dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from sklearn.neighbors import NearestNeighbors
from thefuzz import fuzz
from thefuzz import process
import re
import json
import numpy as np

# Database
movies_df = pd.read_csv('Data/df_reco_final.csv', sep=',') 
    
# FRONT-END
app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

id_increment = 0

#DATA

def get_movies_id(movie_id):
    return movie_id

def display_moviebox(poster, movie_id):
    movies_result_list = []
    movie_id = get_movies_id(movie_id)
    global id_increment
    for i in range(len(poster)):
        id_increment += 1
        movies_result_list.append(
            dbc.Col([
                html.Div([
                    html.A(
                        html.Img(src=poster[i], className='movieposter')
                    ,id=movie_id[i], href='#')
                ], className='moviecard')
            ])
        )
    movies_result_list.insert(0, dbc.Col(width=1))
    movies_result_list.append(dbc.Col(width=1))
    return movies_result_list

def display_target_movie(poster, synopsis, year,name, genre, rating):
    return dbc.Row([
               dbc.Col(width=3),
               dbc.Col(
                    html.Div(
                        html.Img(src=poster, width=170, height=250),
                    ),
                width=2),
        
                dbc.Col([
                    html.P(f'Synopsis:  {synopsis}', \
                           style={'color':'white', 'textAlign':'justify'}),
                    html.P(f'Année: {str(year)}', style={'color':'white', 'textAlign':'justify'}),
                    html.P(f'Acteurs principaux: {name}', style={'color':'white', 'textAlign':'justify'}),
                    html.P(f'Genre: {genre}', style={'color':'white', 'textAlign':'justify'}),
                    html.P(f'Rating: {rating}/10', style={'color':'white', 'textAlign':'justify'}),
                    
                ]),
                dbc.Col(width=3)
            ], style={'marginTop':'30px', 'marginBottom':'30px'})        
        
    

def create_callback_inputs(poster, movie_id):
    callback_inputs_list = []
    movies_html = display_moviebox(poster, movie_id)
    for i in range(1, len(movies_html)-1):
        html_to_str = ''.join(f'{movies_html[i]}')
        callback_inputs_list.append(
            Input(component_id=f"{''.join(re.search(r'(tt)([0-9]+)', html_to_str).groups())}", component_property='n_clicks')
        )
    return callback_inputs_list

pop_movies_df = movies_df.sort_values(by='averageRating', ascending=False).head(6)
pop_movies = display_moviebox([i for i in pop_movies_df['poster_url']], \
                              [i for i in pop_movies_df['tconst']])

create_inputs_pop_movies = create_callback_inputs([i for i in pop_movies_df['poster_url']], \
                                                  [i for i in pop_movies_df['tconst']])

random_movies_df = movies_df.sample(n=6)
random_movies = display_moviebox([i for i in random_movies_df['poster_url']], \
                                 [i for i in random_movies_df['tconst']])

create_inputs_random_movies = create_callback_inputs([i for i in random_movies_df['poster_url']], \
                                                      [i for i in random_movies_df['tconst']])

inputs_list = create_inputs_pop_movies + create_inputs_random_movies

#FRONT-END
app.layout = html.Div([
    
    dbc.Row([
        dbc.Col(  
            html.Img(src = 'https://cdn.cp.adobe.io/content/2/dcx/fc743da5-3037-430d-80e8-df3e83e064e6/rendition/preview.jpg/version/0/format/jpg/dimension/width/size/1200', width = 120), 
                 width = 2, style = {'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '8px'}
        ),
        dbc.Col(
            html.H1(" Bienvenue dans votre cinéma ! "), width= 8, style = {'textAlign':'center', 'marginTop':'60px', 'font-size':'x-large'}
        ),
        dbc.Col(
            html.Img(src = 'https://cdn.cp.adobe.io/content/2/dcx/fc743da5-3037-430d-80e8-df3e83e064e6/rendition/preview.jpg/version/0/format/jpg/dimension/width/size/1200', width = 120), 
                 width = 2, style = {'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '8px'}
        ),    
     ]),
  
    dbc.Row([
        dbc.Col( 
            html.H2(" '' Le meilleur de l'Europe au coeur de la Creuse  ''"), style={'textAlign': 'center', \
                                                                                     'marginTop': '2px', 'marginBottom':'20px'}
        )
    ]),
    
    dbc.Row([
        dbc.Col(width=3), 
        dbc.Col([
            dbc.Input(id="user-search", type="text",
            placeholder = "Veuillez saisir un film ", size ='sm', 
                      style={'marginTop': '20px'}),
        ], width = 6),    
    ]), 
    
    html.Div(id='target-movie'),
    html.Div(id='target-movie2'),
    
    dbc.Row([
        dbc.Col(width=1),
        html.Div(
             html.H5(children='Nous vous recommendons:', style = {'textAlign': 'center'}),
        ),
        
        dbc.Col(width=1),
        html.Div(
            html.H5(id='reco-title'),
        )
    ]),
    
        
    dbc.Row(id='movies-reco-display', className='moviebox'),
                    
    dbc.Row([   
        dbc.Col(width=1),
        dbc.Col(
            html.H5(children = 'Besoin d\'inspirations ? Découvrez nos films à voir ou à revoir', style = {'textAlign': 'center'}),
        ),
        dbc.Col(width=1)
    ]),
    
    dbc.Row(
        pop_movies
    ,className='moviebox'),
    
    dbc.Row([   
        dbc.Col(width=1),
        dbc.Col(
            html.H5(children='Films aléatoires', style = {'textAlign': 'center'}),
        ),
        dbc.Col(width=1)
    ]),
    
    dbc.Row(
        random_movies
    ,className='moviebox')
        
])   

    
#BACK-END

@app.callback(Output(component_id ='target-movie', component_property ='children'),
              Output(component_id ='target-movie', component_property ='style'),
              Input(component_id ='user-search', component_property ='n_submit'),
              State(component_id ='user-search', component_property ='value'), 
              prevent_initial_call = True)
def cover_movie(n_submit, user_search):
    
    if n_submit:
        if user_search is not None:
            user_search = user_search.strip()
            if user_search not in (''):
                l_movies = movies_df['fr_title'].to_list()
                filtered_df = movies_df.loc[movies_df['fr_title'] == process.extractOne(user_search,l_movies)[0]]
                if filtered_df['synopsis'].isna().to_list()[0]:
                    synopsis = None
                else:    
                    synopsis = filtered_df['synopsis'].to_list()[0][:200] + '...'
                    year =  filtered_df['startYear'].to_list()[0]
                    name = filtered_df['primaryName'].to_list()[0].strip("['']").replace("'","")
                    genre =  filtered_df['genres'].to_list()[0].strip("['']").replace("'","")
                    rating = filtered_df['averageRating'].to_list()[0]
                target_movie = display_target_movie(filtered_df['poster_url'].to_list()[0], \
                                                    synopsis, str(year), name , genre, str(rating))
                
                return target_movie, {'display':'block'}
            else:
                return None, {'display':'none'}
        else:
            raise PreventUpdate
    

@app.callback(
    #Output(component_id ='target-movie2', component_property ='children'),
    Output(component_id ='user-search', component_property ='value'),
    Output(component_id ='user-search', component_property ='n_submit'),
    inputs_list,
    prevent_initial_call = True)
def update_target_movie_on_click(*t):
    ctx = dash.callback_context 
    
    triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    filtered_df = movies_df.loc[movies_df['tconst'] == f'{triggered}']
    
    if filtered_df['synopsis'].isna().to_list()[0]:
        synopsis = None
    else:    
        synopsis = filtered_df['synopsis'].to_list()[0][:400] + '...'
        
    target_movie = display_target_movie(filtered_df['poster_url'].to_list()[0], \
                                        synopsis)
    
    return filtered_df['fr_title'].to_list()[0], 1
                    

@app.callback(Output(component_id ='movies-reco-display', component_property ='children'),
              Output(component_id ='reco-title', component_property ='style'),
              Input(component_id ='target-movie', component_property ='children'),
              Input(component_id ='user-search', component_property ='n_submit'),
              State(component_id ='user-search', component_property ='value'), 
              prevent_initial_call = True)        
def display_movies_main_page(target_movie, n_submit, user_search):
    if n_submit:
        if user_search is not None:
            user_search = user_search.strip()
            if user_search not in (''): 
  
                X = movies_df[['genres_notation']]
                distanceKNN_reco_genres_only = NearestNeighbors(n_neighbors=7).fit(X)
                l_movies = movies_df['fr_title'].to_list()
                nearest = distanceKNN_reco_genres_only.kneighbors(movies_df.loc[movies_df['fr_title'] == process.extractOne(user_search,l_movies)[0], 
                                                                                ['genres_notation']])
                movie_recommended = movies_df.loc[nearest[1][0]][movies_df['fr_title']!= process.extractOne(user_search,l_movies)[0]][:6]
                
                reco_movies = display_moviebox([i for i in movie_recommended['poster_url']], \
                                               [i for i in movie_recommended['tconst']])

                return reco_movies, {'display':'block', 'paddingLeft':'35px'}

            else:
                raise PreventUpdate
        else:
            raise PreventUpdate
        
if __name__ == '__main__':
    app.run_server(debug=True)
    
        
# Lancement de l'application sur mon serveur local
# Code to run app in jupyter lab
# app.run_server(mode='external',port=7098 ,debug=True)  
#app.run_server(mode='external',port=7098 ,debug=True)   
