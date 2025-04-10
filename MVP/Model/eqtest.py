import numpy as np
import sounddevice as sd
import soundfile as sf
import scipy.signal as signal
from equalizerModel import EqualizerModel

class RealTimeEqualizedPlayer:
    def __init__(self, file_path, eq_model: EqualizerModel, blocksize=256, samplerate=44100):
        self.file_path = file_path
        self.eq_model = eq_model
        self.blocksize = blocksize
        self.samplerate = samplerate
        self.audio, self.fs = sf.read(file_path)
        if self.fs != self.samplerate:
            raise ValueError(f"Expected sample rate {self.samplerate}, but got {self.fs}")
        self.position = 0
        self.n_channels = self.audio.shape[1] if self.audio.ndim > 1 else 1
        self.filters = self.eq_model.generate_filters(self.samplerate)

    def _apply_eq(self, block):
        for (b, a, gain_db) in self.filters:
            block = signal.lfilter(b, a, block) * (10 ** (gain_db / 20.0))
        return block

    def _callback(self, outdata, frames, time, status):
        if status:
            print(status)

        if self.position + frames >= len(self.audio):
            chunk = self.audio[self.position:]
            chunk = np.pad(chunk, ((0, frames - len(chunk)), (0, 0)), mode='constant')
            done = True
        else:
            chunk = self.audio[self.position:self.position + frames]
            done = False

        self.position += frames

        if self.n_channels > 1:
            for c in range(self.n_channels):
                chunk[:, c] = self._apply_eq(chunk[:, c])
        else:
            chunk = self._apply_eq(chunk)

        outdata[:] = chunk.reshape(outdata.shape)

        if done:
            raise sd.CallbackStop()

    def play(self):
        with sd.OutputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            channels=self.n_channels,
            callback=self._callback,
        ):
            sd.sleep(int((len(self.audio) / self.samplerate) * 1000))


# TEST ENTRY
if __name__ == '__main__':
    eq = EqualizerModel()
    # Muffle below ~315 Hz
    eq.set_band("Low (20-200 Hz)", gain=-12, hp=20, lp=201)
    eq.set_band("Mid (200-2000 Hz)", gain=-12, hp=202, lp=315)
    eq.set_band("High (2000-20000 Hz)", gain=0, hp=316, lp=20000)

    player = RealTimeEqualizedPlayer(
        file_path="C:/Users/Jo/Documents/ECE Senior Design/MuseEase/Instruments/Guitar/sulG_C4.wav",
        eq_model=eq,
    )
    player.play()
