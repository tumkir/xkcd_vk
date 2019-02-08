import os
from random import randint

import requests
from dotenv import load_dotenv


def get_ramdom_comics():
    latest_comics_number = requests.get(
        'https://xkcd.com/info.0.json').json()['num']
    random_comics_response = requests.get(
        f"https://xkcd.com/{randint(1, latest_comics_number)}/info.0.json").json()
    comics = {'url_img': random_comics_response['img'],
              'title': random_comics_response['alt'], 'num': random_comics_response['num']}
    filename = f"{comics['num']}.png"
    comics_image = requests.get(comics['url_img'])
    with open(filename, 'wb') as file:
        file.write(comics_image.content)
    return comics


def upload_comics_into_group_wall(comics):
    params_upload = {
        'group_id': os.getenv('group_id'),
        'access_token': os.getenv('access_token'),
        'v': 5.92,
    }

    upload_url = requests.get('https://api.vk.com/method/photos.getWallUploadServer',
                              params=params_upload).json()['response']['upload_url']

    with open(f"{comics['num']}.png", 'rb') as image:
        upload_response = requests.post(upload_url, files={'photo': image}).json()

    params_save = {
        'group_id': os.getenv('group_id'),
        'photo': upload_response['photo'],
        'server': upload_response['server'],
        'hash': upload_response['hash'],
        'access_token': os.getenv('access_token'),
        'v': 5.92,
    }

    uploaded_image = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto', data=params_save).json()

    params_publish = {
        'owner_id': -int(os.getenv('group_id')),
        'from_group': 1,
        'message': comics['title'],
        'attachments': f"photo{uploaded_image['response'][0]['owner_id']}_{uploaded_image['response'][0]['id']}",
        'access_token': os.getenv('access_token'),
        'v': 5.92,
    }

    publish_on_wall = requests.get(
        'https://api.vk.com/method/wall.post', params=params_publish)

    remove_image_file(comics)

    return f"Successfully loaded https://vk.com/wall-{os.getenv('group_id')}_{publish_on_wall.json()['response']['post_id']}"


def remove_image_file(comics):
    filename = f"{comics['num']}.png"
    os.remove(filename)


if __name__ == '__main__':
    load_dotenv()
    print(upload_comics_into_group_wall(get_ramdom_comics()))
