import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests


# from googleapiclient.discovery import build
class TokenGenerator:
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

    def playlist_list(self, channelid):
        params = {
            # 'access_token': credentials.token,
            'part': 'snippet,contentDetails',
            'maxResults': 25,
            'channelId': channelid
        }
        headers = {'Accept': 'application/json',
                   'Authorization': f'Bearer {credentials.token}', }
        response = requests.get('https://www.googleapis.com/youtube/v3/playlists', params=params, headers=headers)
        return response

    def playlist_create(self, title):
        url = 'https://www.googleapis.com/youtube/v3/playlists'
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
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }
        response = requests.post(url=url, params=params, headers=headers, json=payload)
        return response

    def playlist_edit(self, id, title, status):
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
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }
        response = requests.put('https://www.googleapis.com/youtube/v3/playlists', params=params, json=payload,
                                headers=headers)
        return response

    def playlist_info(self, id):
        params = {
            'part': 'snippet,contentDetails',
            'id': id
        }
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }
        response = requests.get('https://www.googleapis.com/youtube/v3/playlists', params=params, headers=headers)
        return response

    def playlist_insert(self, playlistid, videoid):
        params = {
            'part': 'snippet'
            # 'id':'UCykImLEqjQ2HZAEerN9wzjw',

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
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }
        response = requests.post('https://www.googleapis.com/youtube/v3/playlistItems', params=params, headers=headers,
                                 json=payload)
        return response

    def playlist_delete_item(self, id):
        params = dict(
            part='id'
        )
        payload = dict(
            id=id
        )
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }
        response = requests.delete('https://www.googleapis.com/youtube/v3/playlistItems', params=params,
                                   headers=headers, json=payload)
        return response

    def playlist_items_info(self, playlistid):
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }

        next_page_token = ''
        results = []

        while next_page_token is not None:
            params = dict(
                part="snippet,contentDetails",
                playlistId=playlistid,
                pageToken=next_page_token
            )

            response = requests.get('https://www.googleapis.com/youtube/v3/playlistItems', params=params,
                                    headers=headers)
            # for item in response.json()['items']:
            # results.append(item)
            results.append(response)
            next_page_token = response.json().get('nextPageToken')
        return results

    def playlist_delete(self, id):
        params = dict(
            part="id",
        )
        payload = dict(
            id=id
        )
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }
        response = requests.delete('https://www.googleapis.com/youtube/v3/playlists', params=params,
                                   headers=headers, json=payload)
        return response

    def playlist_clone(self, origin_id):
        new_playlist = self.playlist_create('cloned playlist')
        data_to_transfer = self.playlist_items_info(origin_id)
        for item in data_to_transfer:
            self.playlist_insert(new_playlist.json()['id'], item)
        return new_playlist

    def search(self, keyword, results):
        params = dict(
            part='snippet',
            maxResults=results,
            q=keyword
        )
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }
        response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params, headers=headers)
        return response

    def top_three(self, playlist_id='UCykImLEqjQ2HZAEerN9wzjw'):
        videos = []
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {credentials.token}', }
        if playlist_id == 'UCykImLEqjQ2HZAEerN9wzjw':
            playlists = []
            response = self.playlist_list('UCykImLEqjQ2HZAEerN9wzjw')
            for objects in response.json()['items']:
                playlists.append(objects['id'])
            for playlist_index in playlists:
                for items in self.playlist_items_info(playlist_index):
                    for vids in items.json()['items']:
                        params = {
                            'part': 'snippet, statistics',
                            'id': vids['snippet']['resourceId']['videoId']
                        }
                        response = requests.get('https://www.googleapis.com/youtube/v3/videos', params=params,
                                                headers=headers).json()['items'][0]['statistics']['viewCount']
                        videos.append((int(response), vids['snippet']['resourceId']['videoId']))

        else:
            for items in self.playlist_items_info(playlist_id):
                for vids in items.json()['items']:
                    params = {
                        'part': 'snippet, statistics',
                        'id': vids['snippet']['resourceId']['videoId']
                    }
                    response = \
                        requests.get('https://www.googleapis.com/youtube/v3/videos', params=params,
                                     headers=headers).json()[
                            'items'][0]['statistics']['viewCount']
                    videos.append((int(response), vids['snippet']['resourceId']['videoId']))
        videos = sorted(videos, reverse=True)
        return videos[:3]

    def playlist_merge_n_delete(self, source_id, second_id):
        second_playlist = []
        for items in self.playlist_items_info(second_id):
            for song in items.json()['items']:
                second_playlist.append(song['snippet']['resourceId']['videoId'])
        for to_add in second_playlist:
            self.playlist_insert(source_id, to_add)
        self.playlist_delete(second_id)
