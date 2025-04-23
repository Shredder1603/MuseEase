import numpy as np
import os
import matplotlib.pyplot as plt
import soundfile as sf

class BiquadFilter:
    def __init__(self, filter_type, fs, f0, gain_db=0.0, Q=1.0):
        self.filter_type = filter_type
        self.fs = fs
        self.f0 = f0
        self.gain_db = gain_db
        self.Q = Q

        self._x1 = 0.0
        self._x2 = 0.0
        self._y1 = 0.0
        self._y2 = 0.0

        self._compute_coefficients()

    def _compute_coefficients(self):
        A = 10 ** (self.gain_db / 40)
        omega = 2 * np.pi * self.f0 / self.fs
        alpha = np.sin(omega) / (2 * self.Q)
        cos_omega = np.cos(omega)

        if self.filter_type == 'lowshelf':
            beta = np.sqrt(A) / self.Q
            b0 = A * ((A + 1) - (A - 1) * cos_omega + 2 * beta * np.sin(omega))
            b1 = 2 * A * ((A - 1) - (A + 1) * cos_omega)
            b2 = A * ((A + 1) - (A - 1) * cos_omega - 2 * beta * np.sin(omega))
            a0 = (A + 1) + (A - 1) * cos_omega + 2 * beta * np.sin(omega)
            a1 = -2 * ((A - 1) + (A + 1) * cos_omega)
            a2 = (A + 1) + (A - 1) * cos_omega - 2 * beta * np.sin(omega)

        elif self.filter_type == 'highshelf':
            beta = np.sqrt(A) / self.Q
            b0 = A * ((A + 1) + (A - 1) * cos_omega + 2 * beta * np.sin(omega))
            b1 = -2 * A * ((A - 1) + (A + 1) * cos_omega)
            b2 = A * ((A + 1) + (A - 1) * cos_omega - 2 * beta * np.sin(omega))
            a0 = (A + 1) - (A - 1) * cos_omega + 2 * beta * np.sin(omega)
            a1 = 2 * ((A - 1) - (A + 1) * cos_omega)
            a2 = (A + 1) - (A - 1) * cos_omega - 2 * beta * np.sin(omega)

        elif self.filter_type == 'peak':
            b0 = 1 + alpha * A
            b1 = -2 * cos_omega
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * cos_omega
            a2 = 1 - alpha / A

        else:
            raise ValueError(f"Unsupported filter type: {self.filter_type}")

        # normalize coefficients
        self.b0 = b0 / a0
        self.b1 = b1 / a0
        self.b2 = b2 / a0
        self.a1 = a1 / a0
        self.a2 = a2 / a0
        #print(f"[{self.filter_type.upper()}] fs={self.fs}, f0={self.f0}, gain={self.gain_db}dB, Q={self.Q}")
        #print(f"   Coefficients: b0={self.b0:.6f}, b1={self.b1:.6f}, b2={self.b2:.6f}, a1={self.a1:.6f}, a2={self.a2:.6f}")

    def process(self, x):
        y = self.b0 * x + self.b1 * self._x1 + self.b2 * self._x2 - self.a1 * self._y1 - self.a2 * self._y2
        
        if abs(y) < 1e-10:
            y = 0.0
            
        self._x2 = self._x1
        self._x1 = x
        self._y2 = self._y1
        self._y1 = y

        return np.clip(y, -1.0, 1.0)
    
    def reset(self):
        self._x1 = self._x2 = self._y1 = self._y2 = 0.0

    @classmethod
    def create_low_shelf(cls, fs, f0, gain_db, Q=0.707):
        return cls('lowshelf', fs, f0, gain_db, Q)

    @classmethod
    def create_high_shelf(cls, fs, f0, gain_db, Q=0.707):
        return cls('highshelf', fs, f0, gain_db, Q)

    @classmethod
    def create_mid_shelf(cls, fs, f0, gain_db, Q=1.0):
        return cls('peak', fs, f0, gain_db, Q)

# Independent test routine
def main():
    sample_path = r"C:\Users\Jo\Documents\ECE Senior Design\MuseEase\Instruments\Guitar\SulE_C3.wav"
    if not os.path.exists(sample_path):
        raise FileNotFoundError(f"Guitar sample not found at {sample_path}")

    # Load guitar
    guitar, sr = sf.read(sample_path)
    if guitar.ndim > 1:
        guitar = guitar[:, 0]

    # Generate sine tone (C3 = 130.81 Hz)
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    sine = 0.5 * np.sin(2 * np.pi * 130.81 * t)

    # Create filters
    low = BiquadFilter.create_low_shelf(sr, f0=250, gain_db=6, Q=0.707)
    mid = BiquadFilter.create_mid_shelf(sr, f0=400, gain_db=-6, Q=1.0)
    high = BiquadFilter.create_high_shelf(sr, f0=4000, gain_db=-6, Q=0.707)

    def apply_chain(x):
        for f in (low, mid, high):
            f.reset()
            x = np.array([f.process(i) for i in x])
        return x

    # Apply to both
    sine_boosted = apply_chain(sine)
    guitar_boosted = apply_chain(guitar)

    # Plot
    plt.figure(figsize=(14, 6))
    plt.subplot(2, 1, 1)
    plt.plot(sine[:1000], label="Original Sine")
    plt.plot(sine_boosted[:1000], label="Boosted Sine", alpha=0.7)
    plt.legend()
    plt.title("Sine Tone Before and After EQ")

    plt.subplot(2, 1, 2)
    plt.plot(guitar[:1000], label="Original Guitar")
    plt.plot(guitar_boosted[:1000], label="Boosted Guitar", alpha=0.7)
    plt.legend()
    plt.title("CulE_C3.wav Guitar Before and After EQ")

    plt.tight_layout()
    plt.show()

    # Save audio
    sf.write("original_sine.wav", sine, sr)
    sf.write("boosted_sine.wav", sine_boosted, sr)
    sf.write("boosted_guitar.wav", guitar_boosted, sr)

'''
if __name__ == "__main__":
    main()
'''