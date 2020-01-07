import unittest
import praw
import privatekeys

import testbot as a

real_user = "spez"
fake_user = "jg98438gh9g023f39"  # lets hope this user doesnt exist

real_comment_id = "7cff0b"  # pride and accomplishment
comment_id_bottesting = "dwixky"  # comment found on /r/bottesting
reddit = praw.Reddit(client_id=privatekeys.reddit_client_id,
                     client_secret=privatekeys.reddit_client_secret_key,
                     user_agent='console:testbot:1.0.0 (by /u/deltatwister)',
                     username=privatekeys.username,
                     password=privatekeys.password)



class MyTestCase(unittest.TestCase):

    def setUpClass(cls) -> None:
        submission = reddit.get_submission(url=real_comment_id)

    def test_is_a_real_user(self):
        self.assertFalse(a.is_a_real_user(fake_user))
        self.assertTrue(a.is_a_real_user(real_user))

    def test_enqueue_comment(self):
        a.enqueue_comment(real_comment_id)
        a.enqueue_comment(comment_id_bottesting)
        self.assertEqual(a.dequeue(), real_comment_id)
        self.assertEqual(a.dequeue(), comment_id_bottesting)


if __name__ == '__main__':
    unittest.main()
