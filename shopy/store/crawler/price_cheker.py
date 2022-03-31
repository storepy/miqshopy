import asyncio


class Tracker:
    def __init__(self, *args, **kwargs):
        print('Start')

    async def get_items(self):
        print('Getting prduct items')
        # make api call
        # add


class Item:
    type = None
    url = None
    cost = None

    def __init__(self, type=None, url=None, cost=None, ** kwargs):
        self.type = type
        self.url = url
        self.cost = cost


class ItemTracker:
    slugs = []
    q = asyncio.Queue()
    boot = asyncio.Event()

    def __init__(self, *args, **kwargs):
        print('Item tracker start')

    async def crawl(self):
        print('Crawling: Waiting for activation')

        await self.boot.wait()
        print('Crawling: Start')

        while True:
            item = await self.q.get()  # type: Type[Item]
            # self.q.task_done()
            # check last updated > 10h
            # yes: crawl item data, validate cost, if less update
            # no: add to back of q

    async def add_item(self, data: dict):
        item = Item(**data)
        await self.q.put(item)

    async def remove_item(self, item):
        self.slugs.remove(item.slug)
        # await self.q.task_done()


i = {'type': 'mytype', 'url': 'myurl'}
ii = Item(**i)

print(ii.url)
