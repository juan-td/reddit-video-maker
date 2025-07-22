import praw
import json

try:
    with open("client_details.json", "r") as file:
        data = json.load(file)
except Exception as e:
    print("[ERROR]: Cannot find file client_details.json")
    exit(1)

reddit = praw.Reddit(
    client_id=data["client_id"],
    client_secret=data["client_secret"],
    user_agent=data["user_agent"],
)


def get_posts(sub, count, span):
    subreddit = reddit.subreddit(sub)
    posts = []

    submissions = subreddit.top(time_filter=span, limit=count)

    for submission in submissions:
        if "r/" not in submission.title and "reddit" not in submission.title:
            posts.append(submission)

    posts.reverse
    return posts


def get_post_url(url):
    post_id = url.split("/")[-2]
    posts = []

    submissions = [reddit.submission(post_id)]

    for submission in submissions:
        if "r/" not in submission.title and "reddit" not in submission.title:
            posts.append(submission)

    posts.reverse
    return posts


def get_comments(submission):
    submission.comment_sort = "best"

    comments = []

    for top_level_comment in submission.comments:
        # make sure it's not a link and get top 6 comments
        if "http" not in top_level_comment.body and len(comments) < 6:
            comments.append(top_level_comment)
        elif len(comments) >= 6:
            break

    return comments


## For question reply videos
def scrapeComments(subreddit, count, span) -> list:
    try:
        posts = get_posts(subreddit, count, span)
    except:
        print(
            "[ERROR]: Client could not connect to Reddit. Please check application details"
        )
        return [None]

    all_comments = []

    for post in posts:
        got_comments = get_comments(post)

        for comment in got_comments:
            if len(comment.body) > 1200:
                got_comments = [comment]
                break
        comments = [post]
        length = 0
        # return as many comments that are under 1000 characters (~200 words)
        for comment in range(len(got_comments)):
            length += len(got_comments[comment].body)
            if length > 2000 and comment > 0:
                break
            else:
                comments.append(got_comments[comment])

        all_comments.append(comments)

    return all_comments


## For long form story videos
def scrapeText(subreddit, count, span, video_type="lf", url=None):
    if video_type == "url":
        posts = get_post_url(url)
    else:
        posts = get_posts(subreddit, count, span)
    postText = []

    for i in range(count):
        postText.append([posts[i], posts[i].selftext])

    return postText


if __name__ == "__main__":
    scrapeComments("askreddit", 1, "day")
    scrapeText("nosleep", 1, "day")
