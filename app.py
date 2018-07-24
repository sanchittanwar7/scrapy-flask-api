import json
from flask import Flask, request
from scrapy.crawler import CrawlerRunner
from tripadvisor import TripAdvisor
from trip2 import Trip2Spider

app = Flask('Scrape With Flask')
crawl_runner = CrawlerRunner()      # requires the Twisted reactor to run
reviews_list = []                    # store quotes
scrape_in_progress = False
scrape_complete = False


@app.route('/greeting')
@app.route('/greeting/<name>')
def greeting(name='World'):
    return 'Hello %s!' % (name)

@app.route('/crawl')
def crawl_for_quotes():
    global scrape_in_progress
    global scrape_complete

    location = request.args.get("location")

    if not scrape_in_progress:
        scrape_in_progress = True
        global quotes_list
        eventual = crawl_runner.crawl(TripAdvisor , location=location, reviews_list=reviews_list)
        eventual.addCallback(finished_scrape)
        return 'SCRAPING'
    elif scrape_complete:
        return 'SCRAPE COMPLETE'
    return 'SCRAPE IN PROGRESS'

@app.route('/attractions')
def crawl_for_attractions():
    global scrape_in_progress
    global scrape_complete

    location = request.args.get("location")

    if not scrape_in_progress:
        scrape_in_progress = True
        global quotes_list
        eventual = crawl_runner.crawl(Trip2Spider , location=location, reviews_list=reviews_list)
        eventual.addCallback(finished_scrape)
        return 'SCRAPING'
    elif scrape_complete:
        return 'SCRAPE COMPLETE'
    return 'SCRAPE IN PROGRESS'

@app.route('/results')
def get_results():
    global scrape_complete
    if scrape_complete:
        return json.dumps(reviews_list)
    return 'Scrape Still Progress'

def finished_scrape(null):
    global scrape_complete
    scrape_complete = True


if __name__=='__main__':
    from sys import stdout

    from twisted.logger import globalLogBeginner, textFileLogObserver
    from twisted.web import server, wsgi
    from twisted.internet import endpoints, reactor

    globalLogBeginner.beginLoggingTo([textFileLogObserver(stdout)])

    root_resource = wsgi.WSGIResource(reactor, reactor.getThreadPool(), app)
    factory = server.Site(root_resource)
    http_server = endpoints.TCP4ServerEndpoint(reactor, 9000)
    http_server.listen(factory)

    reactor.run()

