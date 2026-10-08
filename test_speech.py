from ai.speech_to_text import transcribe_audio


audio_file = "multilingual_conversation.wav"

transcript = transcribe_audio(audio_file)

print("\n--- TRANSCRIPT ---")
print(transcript)