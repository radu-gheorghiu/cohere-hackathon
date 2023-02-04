import json
from googleapiclient.discovery import build

# Developer key for the YouTube API
DEVELOPER_KEY = "YOUR_API_KEY"
# YouTube API service name
YOUTUBE_API_SERVICE_NAME = "youtube"
# YouTube API version
YOUTUBE_API_VERSION = "v3"


class YouTubeAPI:
    def __init__(self):
        """
        Initializes the YouTube API client
        """
        self.youtube = build(
            YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY
        )

    def _get_comments(self, video_id, next_page_token=None):
        """
        Retrieves top-level comments for a given video.

        Parameters:
            video_id (str): ID of the video
            next_page_token (str): token for the next set of comments

        Returns:
            results
        """
        results = (
            self.youtube.commentThreads()
            .list(
                part="id,snippet,replies",
                maxResults=100,
                videoId=video_id,
                textFormat="plainText",
                pageToken=next_page_token,
            )
            .execute()
        )
        return results

    def _get_replies(self, parent_id, next_page_token=None):
        """
        Retrieve replies for a given comment

        Parameters:
            comment_id: list of comma separeted ID's of the top comments
            next_page_token: token for the next set of replies

        Returns:
            results
        """
        results = (
            self.youtube.comments()
            .list(
                part="snippet",
                parentId=parent_id,
                maxResults=100,
                textFormat="plainText",
                pageToken=next_page_token,
            )
            .execute()
        )
        return results

    def fetch_comment_threads(self, video_id):
        comments_with_replies = []
        comments_data = []
        next_page_token = None

        while True:
            # Retrieve top-level comments
            comments = self._get_comments(video_id, next_page_token)
            for item in comments["items"]:
                comment = item["snippet"]["topLevelComment"]
                comment_id = item["id"]
                total_reply_count = item["snippet"]["totalReplyCount"]
                comments_data.append(
                    {
                        comment_id: {
                            "author": comment["snippet"]["authorDisplayName"],
                            "text": comment["snippet"]["textDisplay"],
                            "likeCount": comment["snippet"]["likeCount"],
                            "totalReplyCount": total_reply_count,
                            "publishedAt": comment["snippet"]["publishedAt"],
                        }
                    }
                )

                if total_reply_count > 0:
                    # add top level commenent ids to list only when fetched replies less than total
                    if total_reply_count > len(item["replies"]["comments"]):
                        comments_with_replies.append(item["id"])
                    else:  # add only fetched replies equals total number of replies
                        # comments_data[comment_id]['replies'] = {}
                        for reply in item["replies"]["comments"]:
                            reply_id = reply["id"].split(".")[1]
                            comments_data.append(
                                {
                                    reply_id: {
                                        "parentId": comment_id,
                                        "author": reply["snippet"]["authorDisplayName"],
                                        "text": reply["snippet"]["textDisplay"],
                                        "likeCount": reply["snippet"]["likeCount"],
                                        "publishedAt": comment["snippet"]["publishedAt"],
                                    }
                                }
                            )
            # Update the token for the next set of comments
            next_page_token = comments.get("nextPageToken")
            # Exit the loop if there are no more comments
            if next_page_token is None:
                break

        for parent_comment_id in comments_with_replies:
            while True:
                # Token for the next set of replies
                next_page_token_replies = None
                replies = self._get_replies(
                    parent_id=parent_comment_id, next_page_token=next_page_token_replies
                )
                # comments_data[parent_comment_id]['replies'] = {}
                for reply in replies["items"]:
                    # parent_id = reply['snippet']['parentId']
                    reply_id = reply["id"].split(".")[1]
                    comments_data.append(
                        {
                            reply_id: {
                                "parentId": parent_comment_id,
                                "author": reply["snippet"]["authorDisplayName"],
                                "text": reply["snippet"]["textDisplay"],
                                "likeCount": reply["snippet"]["likeCount"],
                                "publishedAt": reply["snippet"]["publishedAt"],
                            }
                        }
                    )

                # Update the token for the next set of replies
                next_page_token_replies = replies.get("nextPageToken")
                # Exit the loop if there are no more replies
                if next_page_token_replies is None:
                    break
        return comments_data
