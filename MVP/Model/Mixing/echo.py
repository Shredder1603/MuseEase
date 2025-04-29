import numpy as np
import copy

def apply_echo(chunks, decay, sample_rate, frame):
    last_echo_chunk = chunks[:frame][:].copy()
    # print(last_echo_chunk)
    last_echo_chunk *= (decay * decay)
    # print(last_echo_chunk)
    
    new_echo_chunk = chunks[frame:frame*2][:].copy()
    new_echo_chunk *= decay
    
    new_echo_chunk = np.vstack((new_echo_chunk, last_echo_chunk))

    for chunk in range(2, 5):
        last_echo_chunk = new_echo_chunk
        last_echo_chunk *= decay
        #print(last_echo_chunk)
        
        new_echo_chunk = chunks[chunk*frame:(chunk+1)*frame][:].copy()
        new_echo_chunk *= decay
        #print(new_echo_chunk)
        
        new_echo_chunk = np.vstack((new_echo_chunk, last_echo_chunk))
        
    return new_echo_chunk

# if __name__ == "__main__":
#     frame = 25
#     total_chunks = 5
#     decay = 0.5
#     sample_rate = 44100
#     chunks = np.ones((4, 25)).astype(float)
    
#     print("Original Chunks:\n", chunks)

#     echoed = apply_echo(chunks, decay, sample_rate, frame)

#     print("\nEchoed Output:\n", echoed)
