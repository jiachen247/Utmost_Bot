import webapp2
import logging


class TestPage(webapp2.RequestHandler):
    def get(self):
        logging.debug("here i am")
        self.response.write("hello world")


app = webapp2.WSGIApplication([
    ('/run-unit-test', TestPage)
], debug=True)
