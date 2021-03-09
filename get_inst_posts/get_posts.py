from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import json
import datetime
import re

PAUSE = 5
INSTAGRAM_URL = 'https://www.instagram.com'


def get_posts(username, password, target):
    browser = _login(username, password)
    time.sleep(PAUSE)

    user_id = _get_user_id(browser, target)
    result = _get_next_posts(browser, user_id, "")
    _save_file(target, result)

    browser.close()
    browser.quit()

    return f'{len(result)} posts in last 30 days'


def _login(username, password):
    browser = webdriver.Chrome('./chromedriver')
    try:
        browser.get(INSTAGRAM_URL)
        time.sleep(PAUSE)
        username_input = browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(username)

        password_input = browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        return browser
    except Exception as ex:
        print(ex)
        browser.close()
        browser.quit()


def _get_user_id(browser, target):
    browser.get(f'{INSTAGRAM_URL}/{target}/?__a=1')
    time.sleep(PAUSE)
    data = json.loads(browser.find_element_by_tag_name('pre').text)
    user_id = data['graphql']['user']['id']
    return user_id


def _get_post_comments(browser, post_id):
    browser.get(f'{INSTAGRAM_URL}/p/{post_id}/?__a=1')
    result = []
    data = json.loads(browser.find_element_by_tag_name('pre').text)
    comments = data['graphql']['shortcode_media']['edge_media_to_parent_comment']['edges'] # noqa501
    for comment in comments:
        result.append(comment['node']['text'])
    return result


def _get_next_posts(browser, user_id, end_cursor):
    browser.get(
        f'{INSTAGRAM_URL}/graphql/query/?query_id=17888483320059182&id=' # noqa501
        f'{user_id}&first=12&after={end_cursor}')
    time.sleep(PAUSE)
    date_timestamp = _get_datetime()
    post_data = json.loads(browser.find_element_by_tag_name('pre').text)
    user = post_data["data"]["user"]
    posts = user["edge_owner_to_timeline_media"]["edges"]
    end_cursor = user['edge_owner_to_timeline_media']['page_info']['end_cursor']  # noqa501
    result = []
    is_next = True

    for post in posts:
        timestamp = post["node"]["taken_at_timestamp"]
        if timestamp > date_timestamp:
            url = post["node"]["display_url"]
            post_info = post["node"]["edge_media_to_caption"]["edges"]
            if len(post_info) > 0:
                text = post_info[0]["node"]["text"]
            else:
                text = ""
            likes = post["node"]["edge_media_preview_like"]["count"]
            hashtags = re.findall(r"#(\w+)", text)
            comment_count = post["node"]["edge_media_to_comment"]["count"]
            if comment_count > 0:
                comments = _get_post_comments(browser,
                                             post["node"]['shortcode'])
            else:
                comments = []
            result.append({"url": url, "likes": likes, "text": text,
                           "hashtags": hashtags, "comments": comments})
        else:
            is_next = False
    if is_next is True:
        next_posts = _get_next_posts(browser, user_id, end_cursor)
        return result + next_posts
    return result


def _save_file(target, result):
    with open(f'{target}.json', 'w', encoding="utf8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


def _get_datetime():
    start_date = datetime.datetime.now() - datetime.timedelta(30)
    start_date_timestamp = start_date.timestamp()
    return start_date_timestamp
