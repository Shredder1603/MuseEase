import numpy as np


def linear_gain(pan_position: float):
    """
    :param pan_position: float from -1 to 1 (inclusive) where 1 is left pan and -1 is right pan
    :return: tuple of ints representing the left and right gain to be applied to the respective channels
    """
    l_gain = (1 + pan_position) / 2
    r_gain = (1 - pan_position) / 2
    return l_gain, r_gain


def sine_law_gain(pan_position: float):
    """
    :param pan_position: float from 0 to 1 (inclusive) where 0 is left pan and 1 is right pan
    :return: tuple of ints representing the left and right gain to be applied to the respective channels
    """
    l_gain = np.cos(pan_position * np.pi / 2)
    r_gain = np.sin(pan_position * np.pi / 2)
    return l_gain, r_gain


def constant_power_gain(pan_position: float):
    """
    :param pan_position: float from 0 to 1 (inclusive) where 0 is left pan and 1 is right pan
    :return: tupe of ints representing the left and right gain, corrected for perceived loudness
    """
    angle = pan_position * np.pi / 2
    l_gain = np.sqrt(2) / 2 * (np.cos(angle) + np.sin(angle))
    r_gain = np.sqrt(2) / 2 * (np.cos(angle) - np.sin(angle))
    print(f"pos: {pan_position}")
    return l_gain, r_gain


def m_s_gain(pan_position: float, l_val: np.ndarray, r_val: np.ndarray):

    m_signal = (l_val + r_val) / 2
    s_signal = (l_val - r_val)

    l_pan = 0.5 * (1.0 + pan_position) * m_signal + s_signal
    r_pan = 0.5 * (1.0 + pan_position) * m_signal - s_signal

    return l_pan, r_pan


def pan(pan_type: str, pan_position: float, audio: np.ndarray):
    panned_audio = audio

    if pan_type == "linear":
        l_gain, r_gain = linear_gain(pan_position)
        panned_audio[0] *= l_gain
        panned_audio[1] *= r_gain
    elif pan_type == "sine":
        l_gain, r_gain = sine_law_gain(pan_position / 2 + 0.5)
        panned_audio[0] *= l_gain
        panned_audio[1] *= r_gain
    elif pan_type == "constant":
        l_gain, r_gain = constant_power_gain(pan_position / 2 + 0.5)
        panned_audio[0] *= l_gain
        panned_audio[1] *= r_gain
    elif pan_type == "ms":
        panned_audio = m_s_gain(pan_position, panned_audio[0], panned_audio[1])

    return panned_audio


if __name__ == "__main__":
    import sounddevice as sd
    volume = 0.5
    duration = 2
    time = np.linspace(0, duration, int(44100 * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * time * 440)
    tone2 = 0.5 * np.sin(2 * np.pi * time * 440)
    audio = np.column_stack((tone, tone2))
    sd.play(audio, samplerate=44100)
    sd.wait()
    l_gain, r_gain = constant_power_gain(1)
    panned = audio * np.array([l_gain, r_gain])
    sd.play(panned, samplerate=44100)
    sd.wait()
    l_gain, r_gain = constant_power_gain(0)
    panned = audio * np.array([l_gain, r_gain])
    sd.play(panned, samplerate=44100)
    sd.wait()
