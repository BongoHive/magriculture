from vumi.workers.session.worker import SessionConsumer, SessionPublisher, SessionWorker

class MenuConsumer(SessionConsumer):
    queue_name = "magri.inbound.menu_trans.base" #TODO revise name
    routing_key = "magri.inbound.menu_trans.base" #TODO revise name

class MenuPublisher(SessionPublisher):
    routing_key = "magri.outbound.menu_trans.fallback"

class MenuWorker(SessionWorker):
    pass


