import json

def enrich(movie):
    """ Enrich for search purposes """
    if 'title' in movie:
        movie['title_sent'] = 'SENTINEL_BEGIN ' + movie['title']
    if 'overview' in movie and movie['overview'] is not None:
        movie['overview_sent'] = 'SENTINEL_BEGIN ' + movie['overview']

def reindex(es, movieDict={}, schema='schema.json', index='tmdb'):
    import elasticsearch.helpers
    settings = json.load(open(schema))

    es.indices.delete(index, ignore=[400, 404])
    es.indices.create(index, body=settings)

    def bulkDocs(movieDict):
        for id, movie in movieDict.items():
            if 'release_date' in movie and movie['release_date'] == "":
                del movie['release_date']

            movie['title_len'] = 0
            if 'title' in movie:
                movie['title_len'] = len(movie['title'])

            enrich(movie)
            addCmd = {"_index": index, #E
                      "_type": "movie",
                      "_id": id,
                      "_source": movie}
            yield addCmd
            if 'title' in movie:
                print("%s added to %s" % (movie['title'], index))

    elasticsearch.helpers.bulk(es, bulkDocs(movieDict))

if __name__ == "__main__":
    from elasticsearch import Elasticsearch
    from sys import argv

    esUrl='http://localhost:9200'
    schema='schema.json'
    if len(argv) > 1:
        schema = argv[1]
    es = Elasticsearch(esUrl, timeout=30)
    movieDict = json.loads(open('tmdb.json').read())
    reindex(es, movieDict=movieDict, schema=schema)

