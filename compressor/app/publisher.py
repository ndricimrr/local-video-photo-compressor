class Publisher:
    def __init__(self):
        self.subscribers = []  # List to store subscribers (callback functions)

    # Subscribe a callback function
    def subscribe(self, callback):
        self.subscribers.append(callback)

    # Notify all subscribers (trigger callbacks) with multiple values
    def notify(self, *args):
        for subscriber in self.subscribers:
            subscriber(*args)  # Pass all arguments to the subscriber