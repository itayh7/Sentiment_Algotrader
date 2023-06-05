class RedditPost:
    def __init__(self, title: str, ups: int, downs: int, num_comments: int):
        self.title = title
        self.ups = ups
        self.downs = downs
        self.num_comments = num_comments
        self.sentiment=-1