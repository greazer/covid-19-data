# %% [markdown]
# * Update 04/19/2020 - Added plotly graphs
# * Update 04/15/2020
# * Update 04/14/2020
# * Update 04/13/2020 - Added new cases trend graphs to the start and reordered the graphs (again) to tell a better story as to how the analysis progressed.
# * Update 04/12/2020
# * Update 04/11/2020
# * Update 04/10/2020
# * Updated 04/09/2020 - From what I'm seeing on these graphs, all the cities and states I show here are showing flattening -- except New York, LA and Chicago, with NY still being the worst and not improving at all. At least it's no longer growing exponentially I guess.
# * Looks like the press is starting to ask some of the same questions I'm asking with this analysis:
#     * https://www.mercurynews.com/2020/04/08/how-california-has-contained-coronavirus-and-new-york-has-not/
# * I moved the graphs that negate the effects of city population density to the top, since that's mostly what I've been interested in seeing.
#  %%
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

default_line_thickness=2
default_width = 880
default_height = 550

#  %% [markdown]
# **********************************************************************************************************
# # Setup
# 1. Read in the covid-19-data from nytimes for state and county (https://github.com/nytimes/covid-19-data)
# 2. Pull in a city density table
# 3. Pull in a state density table
# 4. Identify list of states, counties and cities to graph
# **********************************************************************************************************
#  %%
state_cov_data = pd.read_csv('us-states.csv')
county_cov_data = pd.read_csv('us-counties.csv')

population_city_density = pd.read_csv('city_density.csv')
population_city_density = population_city_density.rename(columns={'City': 'citystate', 'Population Density (Persons/Square Mile)': 'density', '2016 Population': 'population', 'Land Area (Square Miles)': 'area'} )
population_city_density[['city', 'state']] = population_city_density.citystate.str.split(', ', expand=True)

population_state_density = pd.read_csv('state_density.csv')
population_state_density = population_state_density.rename(columns={'State': 'state', 'Density': 'density', 'Pop': 'population', 'LandArea': 'area'})

county_cities_east = [
    ['New York', 'New York City', ['New York']],
    ['New Jersey', 'Bergen', ['Newark', 'Jersey City']],
    ['Massachusetts', 'Suffolk', ['Boston']],
    ['South Carolina', 'Charleston', ['Charleston']],
    ['Florida', 'Miami-Dade', ['Miami']],
    ['Florida', 'Broward', ['Fort Lauderdale']],
    ['Florida', 'Duval', ['Jacksonville']]
]
county_cities_west = [
    ['Washington', 'King', ['Seattle']],
    ['Washington', 'Snohomish', ['Everett']],
    ['California', 'Los Angeles', ['Los Angeles']],
    ['California', 'San Francisco', ['San Francisco']],
    ['California', 'San Diego', ['San Diego']],
    ['Texas', 'Harris', ['Houston']],
    ['Texas', 'Bexar', ['San Antonio']],
    ['Texas', 'Dallas', ['Dallas']],
    ['Texas', 'Travis', ['Austin']],
    ['Arizona', 'Maricopa', ['Phoenix']]
]

county_cities_midwest = [
    ['Illinois', 'Cook', ['Chicago']],
    ['Louisiana', 'Orleans', ['New Orleans']],
    ['Ohio', 'Cuyahoga', ['Cleveland']],
    ['Michigan', 'Wayne', ['Detroit']],
    ['Indiana', 'Hamilton', ['Carmel']],
    ['Pennsylvania', 'Philadelphia', ['Philadelphia']]
]

county_cities_east_map = pd.DataFrame(county_cities_east, columns = ['state', 'county', 'cities'])
county_cities_west_map = pd.DataFrame(county_cities_west, columns = ['state', 'county', 'cities'])
county_cities_midwest_map = pd.DataFrame(county_cities_midwest, columns = ['state', 'county', 'cities'])

states_east = county_cities_east_map.state.unique()
states_west = county_cities_west_map.state.unique()
states_midwest = county_cities_midwest_map.state.unique()
states = np.unique(np.concatenate((states_east, states_midwest, states_west)))

# %% [markdown]
# **********************************************************************************************************
# # New cases per day
# This trend line is a moving average of new cases over time.
# **********************************************************************************************************
# %%
def movingaverage(values, window):
    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'valid')
    return sma

def plotnewcases(row, state='US'):
    if (state == 'US'):
        total_cases_by_date = state_cov_data.groupby('date').sum()
        minimum_cases = 100
    else:
        total_cases_by_date = state_cov_data[state_cov_data.state == state].groupby('date').sum()
        minimum_cases = 15

    total_cases_by_date = total_cases_by_date.reset_index()
    total_cases_by_date = total_cases_by_date[total_cases_by_date.cases > minimum_cases]
    delta_cases = total_cases_by_date.cases.to_numpy()[1:] - total_cases_by_date.head(len(total_cases_by_date)-1).cases.to_numpy()[0:]

    delta_cases_ma = movingaverage(delta_cases, 7)
    df = pd.DataFrame(delta_cases_ma, columns=['new'])
    df['days'] = df.index

    fig.add_trace(
        go.Scatter(x=df.days, y=df.new, mode='lines', name=state, line = { 'width': default_line_thickness })
    )

row = 1
layout = go.Layout(
        title = 'New cases by state',
        width=default_width,
        height=default_height
)
fig = go.Figure(layout=layout)
for state in states:
    plotnewcases(row, state)

fig.show()

# %% [markdown]
# **********************************************************************************************************
# # State Totals
# **********************************************************************************************************
# %%
def plottotalcases(row, state, county = 'all'):
    if county == 'all':
        data = state_cov_data[state_cov_data.state == state][['date', 'cases']]
    else:
        data = county_cov_data[county_cov_data.state == state][['date', 'cases', 'county']]
        data = data[county_cov_data.county == county][['date', 'cases']]

    data = data[data.cases >= starting_cases]
    if len(data['cases']):
        data.index = [x for x in range(0, len(data))]

        if (county == 'all'):
            fig.add_trace(
                go.Scatter(x=data.index, y=data.cases, mode='lines', name=state, line = { 'width': default_line_thickness })
            )
        else:
            fig.add_trace(
                go.Scatter(x=data.index, y=data.cases, mode='lines', name=county + ', ' + state, line = { 'width': default_line_thickness })
            )

row += 1
layout.title = 'Total cases by state'
fig = go.Figure(layout=layout)

starting_cases = 1000
for s in states:
    plottotalcases(row, s)

fig.show()

#  %% [markdown]
# **********************************************************************************************************
# # County Totals
# **********************************************************************************************************
row += 1
layout.title = 'Total cases by county'
fig = go.Figure(layout=layout)
starting_cases = 200

for dataset in [county_cities_east_map, county_cities_midwest_map, county_cities_west_map]:
    starting_cases = 200
    for p in dataset.itertuples():
        plottotalcases(row, p.state, p.county)

fig.show()

#  %% [markdown]
# **********************************************************************************************************
# # State cases adjusted for population
# To better get a sense of how different states may be handling the virus outbreak, you can
# adjust the graphs to account for the number of people who live in each state. A state that has
# 100,000 people vs 8,000,000 people will obviously look far better with regard to total cases
# because they have 80x less people. By factoring in the population of a state, this is difference
# is accounted for.
#
# This graph indicates that New York, New Jersey, and Louisiana, are getting far more cases per day
# than the other states, regardless of how many people live in each state.
# **********************************************************************************************************
#  %%
def stateplotpercapita(row, state):
    data = state_cov_data[state_cov_data.state == state][['date', 'cases']]
    data = data[data.cases >= starting_cases]
    state_population = population_state_density[population_state_density.state == state]
    if len(state_population):
        data.index = [x for x in range(0, len(data))]
        plotdata = data.cases / state_population.population.values[0]
        if len(data['cases']):
            fig.add_trace(
                go.Scatter(x=data.index, y=data.cases, mode='lines', name=state, line = { 'width': default_line_thickness })
            )

row += 1
layout.title = 'Total State Cases adjusted for population'
fig=go.Figure(layout=layout)

for dataset in [states_east, states_midwest, states_west]:
    starting_cases = 1000
    for s in dataset:
        stateplotpercapita(row, s)
fig.show()

#  %% [markdown]
# **********************************************************************************************************
# # State cases adjusted for population density
#
# Each state has a population and an area in which this population lives. *Pretend* for a moment that Texas only has 100,000
# people total. Also *pretend* that Rhode Island has 100,000 people. However, you also know that the
# land area of Rhode Island is much, much smaller than that of Texas. So, if Rhode Island gets 5,000 cases of the virus
# and Texas also gets 5,000 case, then you can say with high confidence that the people in Texas are likely completely
# ignoring advice to keep a minimum distance from others. I mean how else could they have the same number of cases as Rhode Island
# where the same number of people are packed together?
#
# This graph removes this consideration from the comparison between states. As you can see, New Jersey is doing far worse than
# than Ohio, Washington and California.
# **********************************************************************************************************
#  %%
def stateplotbydensity(row, state):
    data = state_cov_data[state_cov_data.state == state][['date', 'cases']]
    data = data[data.cases >= starting_cases]
    state_density = population_state_density[population_state_density.state == state]
    if len(state_density):
        data.index = [x for x in range(0, len(data))]
        plotdata = data.cases / state_density.density.values[0]
        if len(data['cases']):
            lastindex = len(data) - 1
            fig.add_trace(
                go.Scatter(x=data.index, y=data.cases, mode='lines', name=state, line = { 'width': default_line_thickness })
            )

row += 1
layout.title = 'Total State Cases adjusted for population density'
fig=go.Figure(layout=layout)

for dataset in [states_east, states_midwest, states_west]:
    starting_cases = 200
    for s in dataset:
        stateplotbydensity(row, s)
fig.show()

#  %% [markdown]
# **********************************************************************************************************
# # City total cases adjusted for population density
# This graph shows that even though Detroit Michigan's population density is around 5x less than that of New York City,
# the number of virus cases is growing there far faster than even New York and New Orleans (which both suck!). I'd be much
# more worried if I lived in Detroit right now.
#
# Note that Cleveland and Seattle, and Los Angeles are pretty flat, which is good.
# **********************************************************************************************************
#  %%
def cityplotbydensity(row, state, city):
    county = 'not found'
    for x in dataset.itertuples():
        if city in x.cities and state == x.state:
            county = x.county

    data = county_cov_data[county_cov_data.state == state][county_cov_data.county == county][['date', 'cases']]
    data = data[data.cases >= starting_cases]
    city_density = population_city_density[population_city_density.state == state][population_city_density.city == city]
    if (len(city_density)):
        data.index = [x for x in range(0, len(data))]
        plotdata = data.cases / city_density.density.values[0]
        if len(data['cases']):
            lastindex = len(data) - 1
            fig.add_trace(
                go.Scatter(x=data.index, y=data.cases, mode='lines', name=city + ', ' + state, line = { 'width': default_line_thickness })
            )

row += 1
layout.title = 'Total City cases adjusted for population density'
fig=go.Figure(layout=layout)

for dataset in [county_cities_east_map, county_cities_midwest_map, county_cities_west_map]:
    starting_cases = 20
    for p in dataset.itertuples():
        for c in p.cities:
            cityplotbydensity(row, p.state, c)

fig.show()

#  %% [markdown]
# **********************************************************************************************************
# # City deaths adjusted for population density
# **********************************************************************************************************
#  %%
def citydeathsplotbydensity(row, state, city):
    county = 'not found'
    for x in dataset.itertuples():
        if city in x.cities and state == x.state:
            county = x.county

    data = county_cov_data[county_cov_data.state == state][county_cov_data.county == county][['date', 'deaths']]
    data = data[data.deaths >= starting_deaths]
    city_density = population_city_density[population_city_density.state == state][population_city_density.city == city]
    if (len(city_density)):
        data.index = [x for x in range(0, len(data))]
        plotdata = data.deaths / city_density.density.values[0]
        if len(data['deaths']):
            fig.add_trace(
                go.Scatter(x=data.index, y=plotdata.values, mode='lines', name=city + ', ' + state, line = { 'width': default_line_thickness })
            )

row += 1
layout.title = 'Total City deaths adjusted for population density'
fig=go.Figure(layout=layout)
for dataset in [county_cities_east_map, county_cities_midwest_map, county_cities_west_map]:
    starting_deaths = 1
    for p in dataset.itertuples():
        for c in p.cities:
            citydeathsplotbydensity(row, p.state, c)
fig.show()


# %%

