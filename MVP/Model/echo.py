import numpy as np
import sounddevice as sd


def apply_echo(audio: np.ndarray, delay_seconds: float, decay: float, sample_rate: int = 44100):
    delay_samples = int(delay_seconds * sample_rate)
    echoed = np.zeros((audio.shape[0] + delay_samples, audio.shape[1]))
    echoed[:audio.shape[0]] += audio
    echoed[delay_samples:] += audio * decay
    return echoed


if __name__ == "__main__":
    volume = 0.5
    duration = 2
    sample_rate = 44100
    time = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = volume * np.sin(2 * np.pi * time * 440)
    stereo_audio = np.column_stack((tone, tone))

    # Play original tone
    print("Playing original tone...")
    sd.play(stereo_audio, samplerate=sample_rate)
    sd.wait()

    # Apply echo and play
    delay = 0.4  # 400 ms delay
    decay = 0.25  # 50% volume for the echo
    echoed_audio = apply_echo(stereo_audio, delay_seconds=delay, decay=decay, sample_rate=sample_rate)
    print("Playing echoed tone...")
    sd.play(echoed_audio, samplerate=sample_rate)
    sd.wait()
