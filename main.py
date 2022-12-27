import time

import yandex_music.exceptions
from yandex_music import Client

token = ''
def compare(playlist1, playlist2):
    a = client.users_playlists(playlist1).tracks

    b = client.users_playlists(playlist2).tracks

    ids1 = dict()
    for x in a:
        ids1[x.id] = 1
    ids2 = dict()
    for x in b:
        ids2[x.id] = 1

    # print(len(a), len(ids1))
    # print(len(b), len(ids2))
    keys1 = ids1.keys()
    keys2 = ids2.keys()
    print(len(ids1), len(a), sorted(keys1))
    print(len(ids2), len(b), sorted(keys2))

    return keys1 == keys2


def create_buf_playlist():
    buf = client.users_playlists_create('Buf')
    return buf.kind


def copy_without_repeat(from_, to):
    a = client.users_playlists(from_).tracks
    ids1 = set()
    for x in a:
        ids1.add((x.id, x.track.artists[0].id))

    b = client.users_playlists(to).tracks
    ids2 = set()
    for x in b:
        ids2.add((x.id, x.track.artists[0].id))

    to_add = list(ids1 - ids2)
    add_list(to_add, to)


def del_one(playlist, index, rev = 11, cnt = 0):
    if cnt > 25:
        print('error')
        return
    try:
        client.users_playlists_delete_track(kind=playlist, from_=index, to=index+1, revision=rev)
    except yandex_music.exceptions.NetworkError as e:
        a = str(e)
        # print(a)
        start = a.find('actual revision') + 17
        end = a.find('\'', start)
        rev = int(str(a[start:end]))
        # print(rev)
        del_one(playlist, index, rev, cnt+1)


def reduce_playlist_stable(playlist):
    a = client.users_playlists(playlist).tracks
    ids = dict()
    # print(a[0].track.title)
    i = len(a)-1
    for x in reversed(a):
        if not x.id in ids:
            ids[x.id] = [i]
        else:
            del_one(playlist, i)
            # time.sleep(1)
            print(f'track \'{a[i].track.title}\' on place {i} deleted,'
                  f' alredy met on place {ids[x.id][0]} ({a[ids[x.id][0]].track.title})')
        i -= 1


def add_list(list1, to):
    list = list1
    while len(list) > 0:
        # print(len(list), 'left')
        xx = list[0]
        try:
            client.users_playlists_insert_track(to, xx[0], xx[1])
        except yandex_music.exceptions.NetworkError as e:
            a = str(e)
            # print(a)
            start = a.find('actual revision') + 17
            end = a.find('\'', start)
            # print(str(a[start:end]))
            rev = int(str(a[start:end]))
            try:
                client.users_playlists_insert_track(to, xx[0], xx[1], revision=rev)
            except yandex_music.exceptions.NetworkError:
                # print('err')
                pass
            else:
                list.pop(0)
        else:
            list.pop(0)


def erase_playlist(playlist):
    while len(client.users_playlists(playlist).tracks) > 0:
        try:
            client.users_playlists_delete_track(kind=playlist, from_=0, to=len(client.users_playlists(playlist).tracks), revision=11)
        except yandex_music.exceptions.NetworkError as e:
            a = str(e)
            # print(a)
            start = a.find('actual revision') + 17
            end = a.find('\'', start)
            # print(str(a[start:end]))
            rev = int(str(a[start:end]))
            try:
                client.users_playlists_delete_track(kind=playlist, from_=0, to=len(client.users_playlists(playlist).tracks), revision=rev)
            except yandex_music.exceptions.NetworkError:
                pass


def reduce_playlist_unstable(playlist):
    x = create_buf_playlist()
    copy_without_repeat(playlist, x)
    print('\n\n\n-----------------\n\n')
    if compare(playlist,x):
        erase_playlist(playlist)
        copy_without_repeat(x, playlist)
        client.users_playlists_delete(x)
        print('reduced')
    else:
        print('no')

if __name__ == '__main__':
    token = input('Enter token: ')
    try:
        client = Client(token).init()
    except yandex_music.exceptions.NetworkError as e:
        print('token is unavailable')
    else:
        print('authorization done')
    while True:
        case = input('Choose option: \n'
                     '1 - reduce playlist, save order\n'
                     '2 - reduce playlist, without saving order\n'
                     '3 - compare playlist\n'
                     '4 - exit\n'
                     'Option: ')
        if case == '1':
            playlist_id = int(input('Playlist id: '))
            reduce_playlist_stable(playlist_id)
        elif case == '2':
            playlist_id = int(input('Playlist id: '))
            reduce_playlist_unstable()
        elif case == '3':
            playlist1_id = int(input('Playlist 1 id: '))
            playlist2_id = int(input('Playlist 2 id: '))
            compare(playlist1_id, playlist2_id)
        elif  case == 'exit':
            break
        else:
            print('No such option')