"""Week 4, Task 3: congestion control for the simulated bottleneck.

The link has a 20-slot RTT and transmits one packet per slot, so a window of
about 20 packets keeps the pipe full without deliberately building a queue.
"""


class YourControl:
    """A bounded slow-start controller that converges on the link BDP.

    It starts conservatively, opens quickly while there is unused capacity,
    and never intentionally exceeds the 20-packet pipe.  A timeout still
    backs the sender off, so a transient loss cannot leave stale packets in
    flight while the controller continues to open its window.
    """

    TARGET_WINDOW = 20.0
    MIN_WINDOW = 1.0

    def __init__(self):
        self.window = self.MIN_WINDOW

    def on_ack(self):
        """One packet completed a round trip successfully."""
        # Increasing by one for each ACK is slow start.  The cap is important:
        # a larger window only fills the 10-packet tail-drop queue here.
        if self.window < self.TARGET_WINDOW:
            self.window = min(self.TARGET_WINDOW, self.window + 1.0)

    def on_loss(self):
        """A timeout indicates a packet did not complete its round trip."""
        # A modest multiplicative decrease drains any transient backlog.  ACKs
        # subsequently restore the BDP-sized target, but never exceed it.
        self.window = max(self.MIN_WINDOW, self.window * 0.8)