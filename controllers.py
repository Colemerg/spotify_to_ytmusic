import time
from datetime import datetime

import spotipy

from spotify_to_ytmusic.setup import setup as setup_func
from spotify_to_ytmusic.spotify import Spotify
from spotify_to_ytmusic.ytmusic import YTMusicTransfer


def _get_spotify_playlist(spotify, playlist):
    try:
        return spotify.getSpotifyPlaylist(playlist)
    except Exception as ex:
        print(
            "Could not get Spotify playlist. Please check the playlist link.\n Error: "
            + repr(ex)
        )
        return


def _print_success(name, playlistId):
    print(
        f"Success: created playlist '{name}' at\n"
        f"https://music.youtube.com/playlist?list={playlistId}"
    )


def _init():
    return Spotify(), YTMusicTransfer()


def all(args):
    spotify, ytmusic = _init()
    pl = spotify.getUserPlaylists(args.user)
    print(str(len(pl)) + " playlists found. Starting transfer...")
    count = 1
    for p in pl:
        print("Playlist " + str(count) + ": " + p.get("name", "Bilinmeyen Playlist"))
        count = count + 1
        try:
            playlist = spotify.getSpotifyPlaylist(p.get("external_urls", {}).get("spotify", ""))
            videoIds = ytmusic.search_songs(playlist.get("tracks", []))
            playlist_id = ytmusic.create_playlist(
                p.get("name", "Bilinmeyen Playlist"),
                p.get("description", ""),
                "PUBLIC" if p.get("public", False) else "PRIVATE",
                videoIds,
            )
            if args.like:
                for id in videoIds:
                    ytmusic.rate_song(id, "LIKE")
            _print_success(p.get("name", "Bilinmeyen Playlist"), playlist_id)
        except Exception as ex:
            print(f"Could not transfer playlist {p.get('name', 'Bilinmeyen Playlist')}. {str(ex)}")


def _create_ytmusic(args, playlist, ytmusic):
    date = ""
    if args.date:
        date = " " + datetime.today().strftime("%m/%d/%Y")
    name = args.name + date if args.name else playlist.get("name", "Bilinmeyen Playlist") + date
    info = playlist.get("description", "") if (args.info is None) else args.info
    videoIds = ytmusic.search_songs(playlist.get("tracks", []))
    if args.like:
        for id in videoIds:
            ytmusic.rate_song(id, "LIKE")

    playlistId = ytmusic.create_playlist(
        name, info, "PUBLIC" if args.public else "PRIVATE", videoIds
    )
    _print_success(name, playlistId)


def create(args):
    spotify, ytmusic = _init()
    playlist = _get_spotify_playlist(spotify, args.playlist)
    _create_ytmusic(args, playlist, ytmusic)


def liked(args):
    spotify, ytmusic = _init()
    if not isinstance(spotify.api.auth_manager, spotipy.SpotifyOAuth):
        raise Exception("OAuth not configured, please run setup and set OAuth to 'yes'")
    playlist = spotify.getLikedPlaylist()
    _create_ytmusic(args, playlist, ytmusic)


def update(args):
    spotify, ytmusic = _init()
    playlist = _get_spotify_playlist(spotify, args.playlist)
    playlistId = ytmusic.get_playlist_id(args.name)
    videoIds = ytmusic.search_songs(playlist.get("tracks", []))
    if not args.append:
        ytmusic.remove_songs(playlistId)
    time.sleep(2)
    ytmusic.add_playlist_items(playlistId, videoIds)


def remove(args):
    ytmusic = YTMusicTransfer()
    ytmusic.remove_playlists(args.pattern)


def setup(args):
    setup_func(args.file)
