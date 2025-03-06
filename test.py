import sounddevice as sd
import soundfile as sf
import os
import numpy as np
import aifc

if __name__ == "__main__":
    for filename in os.listdir(os.getcwd() + "/Instruments/Piano/"):
        filepath = os.getcwd() + "/Instruments/Piano/" + filename
        data, samplerate = sf.read(filepath)
        max_idx = np.argmax(np.mean(data, axis=1))
        start_frame = 0
        for x in range(max_idx - 1, -1, -1):
            if np.mean(data, axis=1)[x] < 0.001:
                start_frame = x
                break
        end_frame = start_frame + samplerate

        snippet = data[start_frame:end_frame]

        with aifc.open(os.getcwd() + "/Rewrites/Piano/" + filename, "wb") as wf:
            wf.setnchannels(snippet.shape[1])
            wf.setsampwidth(4)
            wf.setframerate(samplerate)
            wf.setnframes(snippet.shape[0])
            wf.writeframes(snippet)

