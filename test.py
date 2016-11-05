#!/usr/bin/env python

import refer
import database
import unittest

USERNAME = 'admin'
PASSWORD = 'secret'

class DataBaseTestCase(unittest.TestCase):
    
    def setUp(self):
        self.database = database.Database()
        self.database.collection = self.database.client.test.test
        self.collection = self.database.collection

    def tearDown(self):
        self.collection.remove()

    def add_post(self):
        self.database.add_post('Title of the post', 'Content', 'test')

    def add_comment(self, url):
        self.database.add_comment(url, 'steve', 'steve@example.org', 'comment')

    def test_add_post(self):
        '''Test adding a blogpost'''
        self.assertTrue(self.collection.count() == 0)
        self.add_post()

        self.assertTrue(self.collection.count() == 1)

    def test_add_comment(self):
        '''Test adding of comments'''
        self.add_post()
        post = self.collection.find_one()
        self.assertTrue( len(post['comments']) == 0)
        self.add_comment(post['url'])
        post = self.collection.find_one()
        self.assertTrue(len(post['comments']) == 1)
        
        

class ReferTestCase(unittest.TestCase):
    
    def setUp(self):
        # refer.db.client = database.Database().client = pymongo.MongoClient()
        refer.db.collection = refer.db.client.test.test
        self.client = refer.app.test_client()
        refer.app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        refer.db.collection.remove()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def add_post(self, title, post, tags):
        return self.client.post('/add-post', data=dict(title=title, post=post, tags=tags),
                        follow_redirects=True)

    def add_comment(self, url, author, email, comment):
        return self.client.post('/add-comment/{0}'.format(url), 
                            data=dict(author=author, email=email, comment=comment), 
                            follow_redirects=True)

    def test_no_posts(self):
        '''No posts in database and nothing on index site'''
        response = self.client.get('/')
        self.assertTrue(b'No posts so far' in response.data)

    def test_login_logout(self):
        '''Logging in and out'''
        response = self.login(USERNAME, PASSWORD)
        print(response.status_code)
        self.assertTrue(b'You were successfully logged in' in response.data)
        response = self.logout()
        self.assertTrue(b'You were logged out' in response.data)
        response = self.login('wrong user', PASSWORD)
        # print(response.data.decode('utf-8'))
        self.assertTrue(b'Invalid login data' in response.data)
        response = self.login(USERNAME, 'wrong password')
        self.assertTrue(b'Invalid login data' in response.data)

    def test_add_post(self):
        '''Adding a post'''
        self.login(USERNAME, PASSWORD)
        response = self.add_post('Title', 'Content', 'tag1 tag2')
        self.assertTrue(b'No posts so far' not in response.data)
        self.assertTrue(b'Title' in response.data)
        self.assertTrue(b'Content' in response.data)
        self.assertTrue(b'tag1' not in response.data)
        self.assertTrue(b'tag2' not in response.data)

        response = self.client.get('/posts/title', follow_redirects=True)
        self.assertTrue(b'tag1' in response.data)
        self.assertTrue(b'tag2' in response.data)

    def test_add_comment(self):
        '''Adding comment'''
        self.login(USERNAME, PASSWORD)
        self.add_post('Title', 'Content', 'tag1 tag2')
        response = self.add_comment('title', 'commentjoe', 'commentjoe@example.org', 'my comment')
        self.assertTrue(b'commentjoe' in response.data)
        self.assertTrue(b'commentjoe@example.org' not in response.data)
        self.assertTrue(b'my comment' in response.data)
        
    

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(DataBaseTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(ReferTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

