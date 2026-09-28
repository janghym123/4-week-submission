class Sender:
    def __init__(self, data_channel, ack_channel, data):
        self.data_channel = data_channel
        self.ack_channel = ack_channel
        self.packets = [
            ("DATA", seq, data[offset:offset + PAYLOAD])
            for seq, offset in enumerate(range(0, len(data), PAYLOAD))
        ]
        self.next_seq = 0
        self.sent_current = False

    def step(self):
        # 끝 패킷까지 ACK를 받았다.
        if self.next_seq >= len(self.packets):
            return False

        # ACK 채널에서 온 패킷 하나를 확인한다.
        ack = self.ack_channel.receive()
        if ack is not None:
            kind, ack_seq = ack

            # 현재 기다리는 패킷의 ACK일 때만 다음으로 진행한다.
            # 중복 ACK 또는 예전 ACK는 무시한다.
            if kind == "ACK" and ack_seq == self.next_seq:
                self.next_seq += 1
                self.sent_current = False

                if self.next_seq >= len(self.packets):
                    return False

        # 처음 전송하거나, 아직 올바른 ACK가 없으면 재전송한다.
        if not self.sent_current or ack is None:
            self.data_channel.send(self.packets[self.next_seq])
            self.sent_current = True

        return True


class Receiver:
    def __init__(self, data_channel, ack_channel):
        self.data_channel = data_channel
        self.ack_channel = ack_channel
        self.expected_seq = 0
        self.received = bytearray()

    def step(self):
        packet = self.data_channel.receive()
        if packet is None:
            return

        kind, seq, payload = packet
        if kind != "DATA":
            return

        # 기대한 순번일 때만 출력에 추가한다.
        # 중복 또는 순서가 앞선 패킷은 다시 추가하지 않는다.
        if seq == self.expected_seq:
            self.received.extend(payload)
            self.expected_seq += 1

        # 새 패킷이든 중복 패킷이든 ACK를 보낸다.
        # ACK가 유실됐을 때 송신자가 재전송해도 다시 ACK할 수 있다.
        self.ack_channel.send(("ACK", seq))

    def data(self):
        return bytes(self.received)