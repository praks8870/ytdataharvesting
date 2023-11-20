**ytdataharvesting**
# YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit

# Introduction

**Hi!!**

Greettings everyone!

Thanks for your attention, 
This is about my project on Youtube data analysis using Google youtube API, MongoDB, PostgreSQL and Streamlit, in Python platform
I have attached the source code in the following jupyter notebooks and python extension file.
In the notebook file you can learn and try out the individual funcions of this project.
And I also used Pandas, Pymongo, psycopg2, google-api-client, streamlit, plotly and streamlit option_menu for this project

I used to do it by step by step by extraction data from youtube using google yutube api key and the youtube channel_id,
First extract the individual data using seperate functions, then modified the code to get the exact data needed.
Then store the extracted data into a data lake called MongoDB.
Then tranform and store the data into a sql server and sto the data into tables.

This code is derived to analyze the sample data scraped from the given channel_id, The scraping data is limited to 50 data for videos and comment data
due to the scraping limitations for youtube api as a free user, However this code can be used to analyze the sample data to give thoughtful
insights to understand how this data scraping and analyzing works.

In the final create sql queries to provide the answers for the asked questions.

# Process

**Python libraries used**

  1.Pandas
  2.psycopg2
  3.Google-api-python-client
  4.Pymongo
  5.Psycopg2
  6.Plotly.express
  7.Streamlit_option_menu

**Coding Steps**

Step-1: Need to import the required libraries.

Step-2: Get your api key for youtube api from google developers console,

Step-3: Extract data from the Youtube channel using the channel id, You can get the channel id from share option in youtube channel wall. Get required details only to avaid errors in the next process

Step-4: Use pymongo client to create a MongoDB database and store the data into it.

Step-5: Create the app using streamlit, Set up the page details by ussing streamlit library.
Streamlit will make the frontend code for you inn simple way.

Step-6: Create SQL tables and Make SQL queries to store the extracted data into tables.

Step-7: Function buttons in streamlit to make good UI.

Step-8: Analyze and visualise the data from SQL tables using Plotly and Pandas.


# Conclution

Please note this is a local derived app, Which will work on local database, 
If you want to run this on your database, Please copy the code and change the database details.

I also given the notebook version to understand the code completely. Try out and give the feedbacks.

You can watch the video of how this project works by clicking here.

#                  THANK YOU
