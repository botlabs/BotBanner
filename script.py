import praw
import requests
import time

# Account settings (private)
USERNAME = ''
PASSWORD = ''

# OAuth settings (private)
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

# Configuration Settings
USER_AGENT = "Bot Banner | /u/YOUR_MAIN_USERNAME_HERE"
AUTH_TOKENS = ["identity", "read", "do_relationship", "modcontributors", "privatemessages"]
EXPIRY_BUFFER = 60

# A list of subs on which to ban users
SUB_LIST = [
"TODO",
"TODO",
"TODO",
]

def get_session_data():
    response = requests.post("https://www.reddit.com/api/v1/access_token",
      auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
      data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD},
      headers = {"User-Agent": USER_AGENT})
    response_dict = dict(response.json())
    response_dict['retrieved_at'] = time.time()
    return response_dict

def get_praw():
    r = praw.Reddit(USER_AGENT)
    r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    session_data = get_session_data()
    r.set_access_credentials(set(AUTH_TOKENS), session_data['access_token'])
    return (r, session_data)

def accept_mod_invites(r):
    for message in r.get_unread():
        if message.body.startswith('**gadzooks!'):
            sr = r.get_info(thing_id=message.subreddit.fullname)
            try:
                sr.accept_moderator_invite()
            except praw.errors.InvalidInvite:
                continue
            message.mark_as_read()

def main(r, session_data):
    EXPIRES_AT = session_data['retrieved_at'] + session_data['expires_in']
    if time.time() >= EXPIRES_AT - EXPIRY_BUFFER:
        raise praw.errors.OAuthInvalidToken
    ##### MAIN CODE #####
    accept_mod_invites(r)
    
    banlist_wiki = r.get_wiki_page("BansAllBots","bannedbots")
    banlist = set([name.strip().lower()[3:] for name in banlist_wiki.content_md.split("\n") if name.strip() != ""])
    
    for subname in SUB_LIST:
        sub = r.get_subreddit(subname)
        for user in list(banlist - set([user.name.lower() for user in sub.get_banned()])):
            sub.add_ban(user)
            print("BAN user.name")

if __name__ == "__main__":
    try:
        print("Retrieving new OAuth token...")
        main(*get_praw())
    except praw.errors.OAuthInvalidToken:
        print("OAuth token expired.")
    except praw.errors.HTTPException:
        print("HTTP error.")
