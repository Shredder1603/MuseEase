import numpy as np

class ReverbProcessor:
    def __init__(self, sample_rate=44100, room_size=0.6, damping=0.1, wet_level=0.5):
        self.sample_rate = sample_rate
        self.room_size = room_size
        self.damping = damping
        self.wet_level = wet_level

        comb_base = [1116, 1188, 1277, 1356]
        self.comb_delays = [int(d * room_size) for d in comb_base]
        self.comb_buffers = [np.zeros(delay) for delay in self.comb_delays]
        self.comb_indices = [0] * len(self.comb_delays)

        allpass_base = [225, 556]
        self.allpass_delays = allpass_base
        self.allpass_buffers = [np.zeros(delay) for delay in self.allpass_delays]
        self.allpass_indices = [0] * len(self.allpass_delays)

    def process(self, audio_chunk):
        audio_chunk = audio_chunk.astype(np.float32)
        comb_out = np.zeros_like(audio_chunk)

        for idx, (buf, delay) in enumerate(zip(self.comb_buffers, self.comb_delays)):
            out = np.zeros_like(audio_chunk)
            for i in range(len(audio_chunk)):
                y = buf[self.comb_indices[idx]]
                buf[self.comb_indices[idx]] = audio_chunk[i] + y * self.damping
                out[i] = y
                self.comb_indices[idx] = (self.comb_indices[idx] + 1) % delay
            comb_out += out

        comb_out /= len(self.comb_delays)

        for idx, (buf, delay) in enumerate(zip(self.allpass_buffers, self.allpass_delays)):
            out = np.zeros_like(comb_out)
            for i in range(len(comb_out)):
                x = comb_out[i]
                y = buf[self.allpass_indices[idx]]
                buf[self.allpass_indices[idx]] = x + y * 0.5
                out[i] = y - x * 0.5
                self.allpass_indices[idx] = (self.allpass_indices[idx] + 1) % delay
            comb_out = out

        return (1 - self.wet_level) * audio_chunk + self.wet_level * comb_out
