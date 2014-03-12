import json

import tornado.web
import tornado.ioloop
import tornado.template

from services import monitor

#
# Base RequestHandler with utility methods
#

class RequestHandler(tornado.web.RequestHandler):
    
    @property
    def user(self):
        return self.get_secure_cookie('user')

    @user.setter
    def set_user(self, user):
        self.set_secure_cookie('user', user)

    @property
    def is_admin(self):
        return auth.is_admin(self.get_secure_cookie('user'))

    @classmethod
    def render(cls, *args, **kw):
        try:
            return cls._template.generate(*args, **kw)
        except AttributeError:
            cls._template = template_loader.load(cls.template)
            return cls._template.generate(*args, **kw)

template_loader = tornado.template.Loader('templates/')

#
# Main page
#

class IndexHandler(RequestHandler):
    template = 'index.html'

    def get(self):
        self.write(self.render())

#
# Challenge presentation and management
#

class ChallengeIndexHandler(RequestHandler):
    template = 'challenge_index.html'

    def get(self):
        self.write(self.render(
            challenges=monitor.challenges
        ))

class ChallengeOverviewHandler(RequestHandler):
    template = 'challenge_overview.html'

    def get(self, challenge):
        status = monitor.status(challenge)
        metadata = monitor.metadata(challenge)
        if not status or not metadata:
            raise tornado.web.HTTPError(404)

        if status['running']:
            status_msg = 'running on %s port %d' % tuple(status['port'])
        elif 'run_type' not in metadata:
            status_msg = 'static'
        else:
            status_msg = 'down'

        self.write(self.render(
            challenge_name=metadata.get('name', challenge),
            challenge_author=metadata.get('author', 'Anonymous'),
            challenge_points=metadata.get('points', 0),
            challenge_description=metadata.get('description', ''),
            challenge_status=status_msg,
        ))

class ChallengeFilesHandler(RequestHandler):

    def get(self, challenge):
        pass # TODO

class ChallengeSubmitHandler(RequestHandler):

    def post(self, challenge):
        metadata = monitor.metadata(challenge)
        if not metadata:
            raise tornado.web.HTTPError(404)

        if isinstance(metadata['flag'], basestring):
            match = metadata['flag'] == self.get_argument('flag')
        else:
            match = self.get_argument('flag') in metadata['flag']

        print match

        self.redirect('/challenges/' + challenge)        

class ChallengeAdminHandler(RequestHandler):
    template = 'challenge_admin.html'

    def get(self, challenge):
        raise tornado.web.HTTPError(403)

    def post(self, challenge):
        raise tornado.web.HTTPError(403)

#
# Scoreboard
#

class ScoreboardHandler(RequestHandler):
    template = 'scoreboard.html'

    def get(self):
        pass # TODO

#
# Users and authentication
#

class UserLoginHandler(RequestHandler):
    
    def get(self):
        pass # TODO
    
    def post(self):
        username = self.get_body_argument('username')
        password = self.get_body_argument('password')
        
        if auth.check_password(username, password):
            self.user = username
            # TODO login successful
        else:
            pass
            # TODO login failed

class UserLogoutHandler(RequestHandler):
    
    def post(self):
        self.user = None

class UserCreateHandler(RequestHandler):

    def get(self):
        raise tornado.web.HTTPError(404)
    
    def post(self):
        raise tornado.web.HTTPError(404)

if __name__ == '__main__':
    app = tornado.web.Application(
        [
            (r'/', IndexHandler),
            (r'/challenges/', ChallengeIndexHandler),
            (r'/challenges/([A-Za-z0-9_-]+)', ChallengeOverviewHandler),
            (r'/challenges/([A-Za-z0-9_-]+)/submit', ChallengeSubmitHandler),
            (r'/challenges/([A-Za-z0-9_-]+)/admin', ChallengeAdminHandler)
        ],
        debug=True,
        static_path='static'
    )
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
