class Cache:
    cached_views = None
    cached_clicks = None
    cached_scores = None

    @staticmethod
    def place_score(client_id, advertiser_id, score):
        if not Cache.cached_scores:  # pragma: no cover
            return
        if client_id not in Cache.cached_scores:
            Cache.cached_scores[client_id] = {advertiser_id: score}
        else:
            Cache.cached_scores[client_id][advertiser_id] = score
