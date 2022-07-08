import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests


# from googleapiclient.discovery import build
class TokenGenerator:
    '''here we will generate our token and we will refresh it'''
    credentials = None

    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)


credentials = TokenGenerator().credentials


class Yt_requests:
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {credentials.token}', }
    base_url = 'https://www.googleapis.com/youtube/v3/'

    def playlist_list(self, channelid):
        '''method that returns a list of playlist for a certain channel id'''
        params = {
            # 'access_token': credentials.token,
            'part': 'snippet,contentDetails',
            'maxResults': 25,
            'channelId': channelid
        }
        response = requests.get(url=self.base_url+'playlists', params=params, headers=self.headers)
        return response

    def playlist_create(self, title):
        '''method that creates a playlist'''
        params = dict(
            part='snippet,status'
        )
        payload = dict(
            snippet=dict(
                title=title,
                description='nothing new'
            ),
            status=dict(
                privacyStatus='public'
            )
        )

        response = requests.post(url=self.base_url+'playlists', params=params, headers=self.headers, json=payload)
        return response

    def playlist_edit(self, id, title, status):
        '''method that lets you edit the title and status of a certain playlist by id'''
        params = {
            'part': 'snippet,status'

        }
        payload = {
            'id': id,
            'snippet': {
                'title': title,
                'description': '.....'
            },
            'status': {
                'privacyStatus': status
            }
        }

        response = requests.put(url=self.base_url+'playlists', params=params, json=payload,
                                headers=self.headers)
        return response

    def playlist_info(self, id):
        '''method that returns info about a playlist'''
        params = {
            'part': 'snippet,contentDetails',
            'id': id
        }

        response = requests.get(url=self.base_url+'playlists', params=params, headers=self.headers)
        return response

    def playlist_insert(self, playlistid, videoid):
        '''method that inserts videos in a playlist'''
        params = {
            'part': 'snippet',

        }

        payload = {
            'snippet': {
                'playlistId': playlistid,
                'position': 0,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': videoid
                }
            }
        }

        response = requests.post(url=self.base_url+'playlistItems', params=params,
                                 headers=self.headers,
                                 json=payload)
        return response

    def playlist_delete_item(self, id):
        '''method that deletes certain items by passing an id'''
        params = dict(
            part='id'
        )
        payload = dict(
            id=id
        )

        response = requests.delete(url=self.base_url+'playlistItems', params=params,
                                   headers=self.headers, json=payload)
        return response

    def playlist_items_info(self, playlistid):
        '''method that returns info about an item from a playlist'''

        next_page_token = ''
        results = []

        while next_page_token is not None:
            params = dict(
                part="snippet,contentDetails",
                playlistId=playlistid,
                pageToken=next_page_token
            )

            response = requests.get(url=self.base_url+'playlistItems', params=params,
                                    headers=self.headers)
            # for item in response.json()['items']:
            # results.append(item)
            results.append(response)
            next_page_token = response.json().get('nextPageToken')
        return results

    def playlist_delete(self, id):
        '''method that deletes a playlist'''
        params = dict(
            part="id",
        )
        payload = dict(
            id=id
        )

        response = requests.delete(url=self.base_url+'playlists', params=params,
                                   headers=self.headers, json=payload)
        return response

    def playlist_clone(self, origin_id):
        '''method that clones a playlist'''
        new_playlist = self.playlist_create('cloned playlist')
        data_to_transfer = self.playlist_items_info(origin_id)
        for item in data_to_transfer:
            self.playlist_insert(new_playlist.json()['id'], item)
        return new_playlist

    def search(self, keyword, maxresults):
        '''method that searches on youtube a maxresults number of items by a keyword'''
        params = dict(
            part='snippet',
            maxResults=maxresults,
            q=keyword
        )
        response = requests.get(url=self.base_url+'search', params=params, headers=self.headers)
        return response

    def top_three(self, playlist_id='UCykImLEqjQ2HZAEerN9wzjw'):
        '''method that returns the top 3 most watched videos of a playlist or from all your playlists'''
        videos = []
        if playlist_id == 'UCykImLEqjQ2HZAEerN9wzjw':
            playlists = []
            response = self.playlist_list(playlist_id)
            for objects in response.json()['items']:
                playlists.append(objects['id'])
            for playlist_index in playlists:
                for items in self.playlist_items_info(playlist_index):
                    for vids in items.json()['items']:
                        params = {
                            'part': 'snippet, statistics',
                            'id': vids['snippet']['resourceId']['videoId']
                        }
                        response = requests.get(url=self.base_url+'videos', params=params,
                                                headers=self.headers).json()['items'][0]['statistics']['viewCount']
                        videos.append((int(response), vids['snippet']['resourceId']['videoId']))

        else:
            for items in self.playlist_items_info(playlist_id):
                for vids in items.json()['items']:
                    params = {
                        'part': 'snippet, statistics',
                        'id': vids['snippet']['resourceId']['videoId']
                    }
                    response = \
                        requests.get(url=self.base_url+'videos', params=params,
                                     headers=self.headers).json()[
                            'items'][0]['statistics']['viewCount']
                    videos.append((int(response), vids['snippet']['resourceId']['videoId']))
        videos = sorted(videos, reverse=True)
        return videos[:3]

    def playlist_merge_n_delete(self, source_id, second_id):
        '''method that merges two playlists and deletes one'''
        second_playlist = []
        for items in self.playlist_items_info(second_id):
            for song in items.json()['items']:
                second_playlist.append(song['snippet']['resourceId']['videoId'])
        for to_add in second_playlist:
            self.playlist_insert(source_id, to_add)
        self.playlist_delete(second_id)
