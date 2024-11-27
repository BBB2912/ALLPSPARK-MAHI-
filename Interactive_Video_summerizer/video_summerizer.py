import streamlit as st
from mediaLoader import MediaLoader
import ffmpeg
from transcriber import AudioTranscriber
from summerizer import TranscriptProcessor

# Initialize the MediaLoader class
media_loader = MediaLoader()



# Sidebar options
st.sidebar.title("Video Options")
option = st.sidebar.radio("Choose an option:", ("Upload Video", "Enter Video Link"))

video_path = None
audio_path=None
final_transcript=None
final_summery=None
sorted_transcript=None
api_key="AIzaSyAgZ618WKny8lEKFSPwMsdxubY5mgNaxgA"

def extract_audio(video_path, audio_path=r"media\audio\temp_audio.wav"):
    try:
        # Use -y to overwrite the output file without asking
        ffmpeg.input(video_path).output(audio_path, format='wav').run(overwrite_output=True, quiet=False)
        audio_path=audio_path
        return audio_path
    except ffmpeg.Error as e:
        print("Error occurred during audio extraction:")
        print(e.stderr.decode())  # Print the error message
        return None

if option == "Upload Video":
    uploaded_file = st.sidebar.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])
    if uploaded_file is not None:
        video_path = media_loader.save_uploaded_video(uploaded_file)
        st.success("Video uploaded and saved as 'uploaded.mp4'.")
        print(audio_path)
        audio_path=extract_audio(video_path)
        st.success("Audio extracted from video.")

elif option == "Enter Video Link":
    video_url = st.sidebar.text_input("Enter the video URL")
    if st.sidebar.button("Download Video"):
        if video_url:
            video_path = media_loader.download_video_from_link(video_url)
            if video_path:
                st.success("Video downloaded and saved as 'downloaded.mp4'.")
            else:
                st.error("Failed to download video. Check the URL and try again.")
        else:
            st.error("Please enter a video URL.")

# Display the video if a path is available
if video_path:
    st.video(video_path)


    

    with st.spinner("transcripting audio"):
        transcriber = AudioTranscriber(audio_path, chunk_length_ms=10000)  # 10 seconds chunks
        transcript=transcriber.process_audio()

        sorted_transcript = sorted(transcript, key=lambda x: x[0])

        final_transcript=""
        for item in sorted_transcript:
            if item[1]!="Could not understand audio.":
                line=f"{item[0]}->{item[1]}\n"
                final_transcript+=line
        print(final_transcript)
        st.header("Transcript")
        # Create a scrollable text area for the transcript
        st.text_area("Transcript", final_transcript, height=300)
    
        processor = TranscriptProcessor(api_key)
        summaries = processor.process_transcript(sorted_transcript, interval=30)
    
        final_summery=""
        for start_time, summary in summaries:
            final_summery+=f"{start_time}s -> {summary}\n"
        st.header("Summary")
        st.text_area("Transcript", final_summery, height=300)

# Exit button to clear files and exit the app
if st.sidebar.button("Exit"):
    media_loader.clear_videos()
    st.success("All video files deleted. You may close the page.")
