import numpy as np

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

    def process(self, x):
        y = self.b0 * x + self.b1 * self._x1 + self.b2 * self._x2 - self.a1 * self._y1 - self.a2 * self._y2

        self._x2 = self._x1
        self._x1 = x
        self._y2 = self._y1
        self._y1 = y

        return np.clip(y, -1.0, 1.0)
    
    @classmethod
    def create_low_shelf(cls, fs, f0, gain_db, Q=0.707):
        return cls('lowshelf', fs, f0, gain_db, Q)

    @classmethod
    def create_high_shelf(cls, fs, f0, gain_db, Q=0.707):
        return cls('highshelf', fs, f0, gain_db, Q)

    @classmethod
    def create_peaking_eq(cls, fs, f0, gain_db, Q=1.0):
        return cls('peak', fs, f0, gain_db, Q)

