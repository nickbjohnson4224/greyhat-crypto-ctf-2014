import os
import json

import tornado.web
import tornado.ioloop
import tornado.template

from services import monitor, auth

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

template_loader = tornado.template.Loader('templates/')

#
# Main page
#

class IndexHandler(RequestHandler):
    template = 'index.html'

    def get(self):
        self.render('templates/index.html')

#
# Challenge presentation and management
#

class ChallengeIndexHandler(RequestHandler):

    def get(self):
        if self.is_admin:
            challenge_list = monitor.challenges
        else:
            challenge_list = monitor.visible_challenges

        self.render('templates/challenge_index.html',
            user='trace',
            selected='challenges',
            challenges=sorted(challenge_list)
        )

class ChallengePageHandler(RequestHandler):

    def get(self, challenge):
        status = monitor.status(challenge)
        metadata = monitor.metadata(challenge)
        if status == None or metadata == None:
            raise tornado.web.HTTPError(404)

        if not self.is_admin and not status['visible']:
            raise tornado.web.HTTPError(404)

        if not self.is_admin:
            if status['running']:
                status_widget = """<div class="box green">Running on %s port %d</div>
                """ % (status['port'][0].upper(), status['port'][1])
            elif 'run_type' not in metadata:
                status_widget = """<div class="box green">Static files only</div>"""
            else:
                status_widget = """<div class="box red">Down for maintainance</div>"""
        else:
            if status['visible']:
                if status['running']:
                    status_widget = """
                    <div class="box green">
                      Running on %s port %d
                      <form method="post">
                        <input type="hidden" name="action" value="stop">
                        <input type="submit" value="Stop" class="submit">
                      </form>
                    </div>
                    """ % (status['port'][0].upper(), status['port'][1])
                elif 'run_type' not in metadata:
                    status_widget = """
                    <div class="box green">
                      Static files only
                      <form method="post">
                        <input type="hidden" name="action" value="hide">
                        <input type="submit" value="Hide" class="submit">
                      </form>
                    </div>
                    """
                else:
                    status_widget = """
                    <div class="box red">
                      Down for maintainance
                      <form method="post">
                        <input type="hidden" name="action" value="start">
                        <input type="submit" value="Start" class="submit">
                      </form>
                      <form method="post">
                        <input type="hidden" name="action" value="hide">
                        <input type="submit" value="Hide" class="submit">
                      </form>
                    </div>
                    """
            else:
                status_widget = """
                <div class="box purple">
                  Hidden
                  <form method="post">
                    <input type="hidden" name="action" value="show">
                    <input type="submit" value="Show" class="submit">
                  </form>
                </div>
                """

        self.render('templates/challenge.html',
            user='trace',
            selected='challenges',
            challenge_files=metadata.get('public_files', []),
            challenge_name=metadata.get('name', challenge),
            challenge_author=metadata.get('author', 'Anonymous'),
            challenge_points=metadata.get('points', 0),
            challenge_solves=42,
            challenge_description=metadata.get('description', ''),
            status=status_widget,
        )

    def post(self, challenge):
        action = self.get_argument('action', None)
        if action == 'start':
            self.action_start(challenge)
        elif action == 'stop':
            self.action_stop(challenge)
        elif action == 'show':
            self.action_show(challenge)
        elif action == 'hide':
            self.action_hide(challenge)
        else:
            raise tornado.web.HTTPError(400)
        self.redirect('')

    def action_start(self, challenge):
        if not self.is_admin:
            raise tornado.web.HTTPError(403)
        monitor.start(challenge)

    def action_stop(self, challenge):
        if not self.is_admin:
            raise tornado.web.HTTPError(403)
        monitor.stop(challenge)

    def action_show(self, challenge):
        if not self.is_admin:
            raise tornado.web.HTTPError(403)
        monitor.show(challenge)

    def action_hide(self, challenge):
        if not self.is_admin:
            raise tornado.web.HTTPError(403)
        monitor.hide(challenge)

class ChallengeFilesHandler(RequestHandler):

    def get(self, challenge, filename):
        self.set_header('Content-Type', 'application/octet-stream')
        self.write(monitor.fetch_file(challenge, filename))

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
            (r'/challenges/?', ChallengeIndexHandler),
            (r'/challenges/([A-Za-z0-9_-]+)', ChallengePageHandler),
            (r'/challenges/([A0Za-z0-9_-]+)/(.*)', ChallengeFilesHandler)
        ],
        debug=True,
        static_path='static',
        cookie_secret=os.urandom(16)
    )
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
