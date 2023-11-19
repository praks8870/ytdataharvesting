import psycopg2
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
import pymongo
from googleapiclient.discovery import build
from PIL import Image

mydb = psycopg2.connect(
    host = "localhost",
    database = "postgres",
    user = "postgres",
    password = "******")

mycursor = mydb.cursor()


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['youtube_data']


API_KEY = 'Your API key'
youtube = build('youtube', 'v3', developerKey=API_KEY)


#use this function to get channel details

def channel_details(channel_id):
    ch_data = []

    request = youtube.channels().list(
        part = "snippet,contentDetails,statistics",
        id = channel_id  # Use the provided channel_id directly
        )
    response = request.execute()

    for i in range(len(response['items'])):
        data = dict(
            channel_id = channel_id,
            channel_name = response['items'][i]['snippet']['title'],
            channel_views = response['items'][i]['statistics']['viewCount'],
            channel_type = response['items'][i]['snippet']['customUrl'],
            channel_description = response['items'][i]['snippet']['description'],
            channel_status = response['items'][i]['snippet']['publishedAt'],
            videos_count = response['items'][i]['statistics']['videoCount']
            )
        ch_data.append(data)
    return ch_data



# use this function to get playlist table data directly
def playlist_data(channel_id):
    pl_data = []

    request = youtube.playlists().list(
        part = "snippet",
        channelId = channel_id,
        # id = playlist_id
    )
    response = request.execute()

    for i in range(len(response['items'])):
        data = dict(channel_id = channel_id,
                    playlist_id = response['items'][i]['id'],
                    playlist_name = response['items'][i]['snippet']['title']
                    )
        
        pl_data.append(data)
    return pl_data


#use this function to get video ids of the channel you entered
def channel_videos(channel_id):
    video_ids = []

    request = youtube.search().list(
        part = "id",
        channelId = channel_id,
        maxResults = 50
    )

    response = request.execute()

    for item in response['items']:
        if 'videoId' in item['id']:
            video_ids.append(item['id']['videoId'])

    return video_ids



#use this function to get comment data from youtube api and table it with anotther function in next step
def comment_data(video_ids):
    cmt_data = []

    request = youtube.commentThreads().list(
        part = 'snippet,replies',
        videoId = video_ids,
        maxResults = 50
        )
    response = request.execute()

    for item in response['items']:
        data = dict(comment_id = item['id'],
                    channel_id = item['snippet']['channelId'],
                    video_id = item['snippet']['videoId'],
                    comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay'],
                    comment_author = item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    comment_published_date = item['snippet']['topLevelComment']['snippet']['publishedAt']
                    )
        cmt_data.append(data)
 
    return cmt_data



#use this function to get video data table details
def video_details(video_ids):
    video_data = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
                    part = "snippet,contentDetails,statistics",
                    id = ','.join(video_ids[i+i:50])
                    )
        response = request.execute()

        for video in response['items']:
            data = dict(channel_name = video['snippet']['channelTitle'],
                        video_id = video['id'],
                        video_name = video['snippet']['title'],
                        channel_id = video['snippet']['channelId'],
                        video_description = video['snippet']['description'],
                        published_date = video['snippet']['publishedAt'],
                        vieew_couunt = video['statistics']['viewCount'],
                        like_count = video['statistics']['likeCount'],
                        favorite_count = video['statistics']['favoriteCount'],
                        comment_count = video['statistics']['commentCount'],
                        duration = video['contentDetails']['duration'],
                        thumbnail = video['snippet']['thumbnails']['default']['url'],
                        caption_status = video['contentDetails']['caption']
                        )

            video_data.append(data)
        return video_data
    

# To get the channel names
def channel_names():   
    ch_name = []
    for i in db.channel_details.find():
        ch_name.append(i['channel_name'])
    return ch_name

#SQL table creation queries
def sql_table_create():

    create_table_query_channels = """
    CREATE TABLE IF NOT EXISTS channels (
        channel_id VARCHAR(255),
        channel_name TEXT,
        channel_views BIGINT,
        channel_type VARCHAR(255),
        channel_description TEXT,
        channel_status TIMESTAMP,
        videos_count INT
        );
    """

    try:
        mycursor.execute(create_table_query_channels)
        mydb.commit()
        print("Tables created successfully.")
    except Exception as e:
        print("Error:", e)
        mydb.rollback()


    create_table_query = """
            CREATE TABLE IF NOT EXISTS videos (
                channel_name TEXT,
                video_id VARCHAR(255),
                video_name TEXT,
                channel_id VARCHAR(255),
                video_description TEXT,
                published_date TIMESTAMP,
                view_count INT,
                like_count INT,
                favorite_count INT,
                comment_count INT,
                duration VARCHAR(255),
                thumbnail TEXT,
                caption_status BOOLEAN);
    """

    try:
        mycursor.execute(create_table_query)
        mydb.commit()
        print("Table created successfully.")
    except Exception as e:
        print("Error:", e)
        mydb.rollback()


    create_table_query_comments = """
    CREATE TABLE IF NOT EXISTS comment_data (
        comment_id VARCHAR(255),
        channel_id VARCHAR(255),
        video_id VARCHAR(255),
        comment_text TEXT,
        comment_author VARCHAR(255),
        comment_published_date TIMESTAMP
    );
    """

    try:
        mycursor.execute(create_table_query_comments)
        mydb.commit()
        print("Tables created successfully.")
    except Exception as e:
        print("Error:", e)
        mydb.rollback()


table = sql_table_create()


#Create a web page on streamlit
icon = Image.open("D:\project\Youtube_logo.png")
st.set_page_config(page_title = "YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit",
                   page_icon = icon,
                   layout = 'wide',
                   initial_sidebar_state = 'expanded',
                   menu_items = {'About': """# This app is used to analyze youtube channel data
                                                Created BY *Prakash*"""})
st.title(" :red[▶️] YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit")

with st.sidebar:
    selected = option_menu(None, ["Home" , "Harvest & Store The Data","View" ],
                            icons = ["house-door-fill","tools", "card-text"],
                            default_index = 0 ,
                            orientation = "v",
                            styles = {"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "0px", 
                                                "--hover-color": "#33A5FF"},
                                   "icon": {"font-size": "30px"},
                                   "container" : {"max-width": "6000px"},
                                   "nav-link-selected": {"background-color": "#33A5FF"}})
    



#Home page configuration
if selected == "Home":
    col1, col2 = st.columns(2, gap = 'medium')
    col1.markdown(" ## :green[Domain] : Social Media" )
    col1.markdown("## :green[Technologies used] : Python,MongoDB, Youtube Data API, MySql, Streamlit")
    col1.markdown("## :green[Overview] : Retrieving the Youtube channels data from the Google API, storing it in a MongoDB as data lake, migrating and transforming data into a SQL database,then querying the data and displaying it in the Streamlit app.")
    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.markdown("#   ")





if selected == "Harvest & Store The Data":
    tab1, tab2 = st.tabs(["$\huge 📝 EXTRACT $", "$\huge 💾 STORE $"])

    #Harvest Data Tab
    with tab1:
        st.markdown("#    ")
        st.write("### Enter the Youtube Channel ID :")
        ch_id = st.text_input("Hint : Goto channel's home page > Right click > View page source > Find channel_id")

        if ch_id and st.button("Harvest Data"):
            ch_details = channel_details(ch_id)
            st.write(f'#### Extracted Data from : green["{ch_details[0]["channel_name"]}"] channel')
            st.table(ch_details)

        if st.button("Upload to MongoDB"):
            with st.spinner("Please wait while we retrive the data for you..."):
                ch_details = channel_details(ch_id)
                video_ids = channel_videos(ch_id)
                vid_details = video_details(video_ids)



                def comments():
                    com_d = []
                    for i in video_ids:
                        com_d += comment_data(i)
                    return com_d
                com_details = comments()
                
# Extract and put the data into Mongodbcopass or Atlas
                collection1 = db.channel_details
                collection2 = db.video_details
                collection3 = db.comment_details


                collection1.insert_many(ch_details)
                collection2.insert_many(vid_details)
                collection3.insert_many(com_details)


                st.success(" Upload to MongoDB successful !!")

    #Transform to SQL Tab
    with tab2:
        st.markdown("#  ")
        st.markdown("### Select a Channel to Begin Transform the Data")
        ch_names = channel_names()
        user_input = st.selectbox("Select Channel", options = ch_names)

        def insert_into_channels():
            collections = db.channel_details
            query = """INSERT INTO channels (channel_id, channel_name, channel_views, channel_type, 
                                             channel_description, channel_status, videos_count) 
                                             values(%s,%s,%s,%s,%s,%s,%s)
                                             """
            
            for i in collections.find({"channel_name" : user_input},{'_id' : 0}):
                            mycursor.execute(query,tuple(i.values()))
                            mydb.commit()

        def insert_into_videos():
            collections1 = db.video_details
            query1 = """INSERT INTO videos (channel_name, video_id, video_name, channel_id, video_description, published_date, view_count, 
                                            like_count, favorite_count, comment_count, duration, thumbnail, caption_status) 
                                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                            """

            for i in collections1.find({"channel_name" : user_input},{'_id' : 0}):
                    values = [str(val).replace("'", "''").replace('"', '""') if isinstance(val, str) else val for val in i.values()]
                    mycursor.execute(query1, tuple(values))
                    mydb.commit()


        def insert_into_comment_data():
            collections1 = db.video_details
            collections2 = db.comment_details
            query2 = """INSERT INTO comment_data (comment_id, channel_id, video_id, comment_text, comment_author,
                                                  comment_published_date) VALUES(%s,%s,%s,%s,%s,%s)
                                                  """

            for vid in collections1.find({"channel_name" : user_input},{'_id' : 0}):
                    for i in collections2.find({'video_id': vid['video_id']},{'_id' : 0}):
                        mycursor.execute(query2,tuple(i.values()))
                        mydb.commit()

        if st.button("Submit"):
            st.balloons()

            try:
                insert_into_videos()
                
                st.success("Video details Transformation to PGSQL Successful !!")
            except:
                st.error("Details already transformed !!")

            try:
                insert_into_comment_data()
                
                st.success("Comment details Transformation to PGSQL Successful !!")
            except:
                st.error("Details already transformed !!")

            try:
                insert_into_channels()
                
                st.success("channel details Transformation to PGSSQL Successful !!")
            except:
                st.error("Details already transformed !!")


                


if selected == "View":
    
    st.write("## :orange[Select any question to get Insights]")
    questions = st.selectbox('Questions',
    ['1. What are the names of all the videos and their corresponding channels?',
    '2. Which channels have the most number of videos, and how many videos do they have?',
    '3. What are the top 10 most viewed videos and their respective channels?',
    '4. How many comments were made on each video, and what are their corresponding video names?',
    '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
    '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
    '7. What is the total number of views for each channel, and what are their corresponding channel names?',
    '8. What are the names of all the channels that have published videos in the year 2022?',
    '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
    '10. Which videos have the highest number of comments, and what are their corresponding channel names?'
    ])
    
    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute("SELECT video_name AS Video_name, channel_name AS Channel_Name FROM videos ORDER BY channel_name")

        col_names = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(mycursor.fetchall(), columns = col_names)
        st.write(df)

        
    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, videos_count AS Total_Videos
                            FROM channels
                            ORDER BY videos_count DESC
                         """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)

        st.write("### :green[Number of videos in each channel :]")

        fig = px.bar(df, x = columns[0], 
                     y = columns[1], 
                     orientation ='v', 
                     color = columns[0]
                     )
        st.plotly_chart(fig, use_container_width = True)

        
    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, video_name AS Video_Title, View_count AS Views 
                            FROM videos
                            ORDER BY views DESC
                            LIMIT 10
                        """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)
        st.write("### :green[Top 10 most viewed videos :]")
        fig = px.bar(df,
                     x = columns[2],
                     y = columns[1],
                     orientation ='h',
                     color = columns[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT video_name, comment_count
                            FROM videos
                            ORDER BY comment_count DESC
                         """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)
          
    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, video_name AS Title, like_count AS Like_Count 
                            FROM videos
                            ORDER BY Like_count DESC
                            LIMIT 10
                        """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)
        st.write("### :green[Top 10 most liked videos :]")
        fig = px.bar(df,
                     x = columns[2],
                     y = columns[1],
                     orientation = 'h',
                     color = columns[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT Video_name AS Title, Like_count AS Like_count
                            FROM videos
                            ORDER BY Like_count DESC
                         """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)
         
    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, channel_views AS Views
                            FROM channels
                            ORDER BY views DESC
                         """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)
        st.write("### :green[Channels vs Views :]")
        fig = px.bar(df,
                     x = columns[0],
                     y = columns[1],
                     orientation = 'v',
                     color = columns[0]
                    )
        st.plotly_chart(fig,use_container_width = True)
        
    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, video_name AS Video_name
                            FROM videos
                            WHERE EXTRACT(YEAR FROM published_date) = 2022
                            GROUP BY channel_name, video_name
                            ORDER BY channel_name, video_name;
                         """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)
        
    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, 
                            ROUND(AVG(EXTRACT(epoch FROM duration::interval)) / 60 ,2) AS "Average_Video_Duration (mins)"
                            FROM videos
                            GROUP BY channel_name
                            ORDER BY "Average_Video_Duration (mins)" DESC;
                         """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)
        st.write("### :green[Avg video duration for channels :]")
        fig = px.bar(df,
                     x = columns[0],
                     y = columns[1],
                     orientation = 'v',
                     color = columns[0]
                    )
        st.plotly_chart(fig,use_container_width = True)
        
    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,video_name AS Video_Name,Comment_count AS Comments
                            FROM videos
                            ORDER BY comments DESC
                            LIMIT 10
                         """)
        data = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(data, columns = columns)
        st.write(df)
        st.write("### :green[Top 10 videos with most comments :]")
        fig = px.bar(df,
                     x = columns[2],
                     y = columns[1],
                     orientation = 'h',
                     color = columns[0]
                    )
        st.plotly_chart(fig,use_container_width = True)


