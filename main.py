import billboard
import pickle, os, subprocess

def load_chart():
    chart = None
    if os.path.isfile("chart.data"):
        with open("chart.data", "rb") as file:
            chart = pickle.load(file)
    else:
        with open("chart.data", "wb") as file:
            chart = billboard.ChartData('pop-songs')
            pickle.dump(chart, file)

    return chart


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = 'AIzaSyAGnBH86i4zyWWTcfidaKTZ_LRreBRI-80'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search(keyword, max_results = 10):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=keyword,
    type='video',
    part='id,snippet',
    maxResults=max_results
  ).execute()

  search_videos = []

  # Merge video ids
  for search_result in search_response.get('items', []):
    search_videos.append(search_result['id']['videoId'])
  video_ids = ','.join(search_videos)

  videos = []

  for id in search_videos:
      videos.append('https://www.youtube.com/watch?v='+ id)


  return videos

def download(url , name):
    import youtube_dl

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }
        ],
    }
    ydl_opts['outtmpl'] = 'tmp/' +name +'.%(ext)s'

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        output = ydl.download([url])

    return "%s.mp3" % name

def trim(filename):

    filter = 'ffmpeg -loglevel 1 -y -i "tmp/%s" -af silenceremove=start_periods=1:start_duration=1:start_threshold=0.06:stop_periods=1:stop_threshold=0.06:stop_duration=2 "filter/%s"' % (filename , filename )

    return_code = subprocess.call(filter, shell=True)

    return return_code  == 0

def copyToFTP():
    cmd = 'cp -r tmp/* /var/ftp/'
    return_code = subprocess.call(cmd, shell=True)
    return return_code == 0


def main():
    chart = load_chart()
    for song in chart:
        name = str(song)
        urls = youtube_search(name)
        if len(urls) < 1:
            continue
        url = urls[0]
        filename = download(url, name)
        trim(filename)

    copyToFTP()
    

if __name__ == '__main__':
    main()
