import librosa 

class AudioLoader:
    """Loads an audio file (wav/mp3/oga) into a mono waveform array."""

    def __init__(self, audio_file):
        self.audio_file = audio_file

    def load(self):
        """Return (y, sr) — audio samples and their native sampling rate."""
        y, sr = librosa.load(self.audio_file, sr=None)
        return y, sr