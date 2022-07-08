import yt_functions
def main():
    yt_tool=yt_functions.Yt_requests()
    '''GET methods:'''
    yt_tool.playlist_items_info(playlistid)
    yt_tool.playlist_list(channelid)
    yt_tool.playlist_info(playlistid)
    yt_tool.search(keyword,no_of_results)
    '''POST methods:'''
    yt_tool.playlist_insert(playlistid,videoid)
    yt_tool.playlist_create(title)
    yt_tool.playlist_edit(playlistid,title,status)
    '''more complex methods using GET, POST and DELETE:'''
    yt_tool.top_three(playlistid)
    yt_tool.playlist_merge_n_delete(mainplaylistid,secondaryplaylistid)
    yt_tool.playlist_delete(playlistid)
    yt_tool.playlist_delete_item(itemid)
    yt_tool.playlist_clone(playlistidtoclone)
if __name__ == '__main__':
    main()