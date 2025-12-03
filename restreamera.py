import subprocess
import signal
import sys

# ==========================
# CONTROL VARIABLES
# ==========================
stream = True   # Master switch: True = streaming on, False = disable all
twitch = True   # Twitch output
kick = True     # Kick output
vlc = True      # Local VLC output

# ==========================
# INPUT AND OUTPUTS
# ==========================
input_stream = "rtmp://192.168.0.113:1935/live/stream"

twitch_url = "rtmp://live.twitch.tv/app/YOUR_TWITCH_KEY"
kick_url   = "rtmp://live.kick.com/app/YOUR_KICK_KEY"
vlc_url    = "rtmp://192.168.0.113:1935/live/vlc"

# ==========================
# BITRATE SETTINGS (optional)
# ==========================
# Set to None to use original bitrate / copy
twitch_video_bitrate = "6000k"  # e.g., 6000 kbps
twitch_audio_bitrate = "160k"

kick_video_bitrate = "6000k"
kick_audio_bitrate = "160k"

vlc_video_bitrate = "4000k"     # Lower for local playback
vlc_audio_bitrate = "128k"

# ==========================
# FUNCTION TO START FFmpeg
# ==========================
def start_ffmpeg(output, transcode_vlc=False, video_bitrate=None, audio_bitrate=None):
    if transcode_vlc or video_bitrate or audio_bitrate:
        cmd = ["ffmpeg", "-i", input_stream]

        # Video
        if transcode_vlc or video_bitrate:
            cmd += ["-c:v", "libx264"]
            cmd += ["-preset", "veryfast"]
            if video_bitrate:
                cmd += ["-b:v", video_bitrate]
        else:
            cmd += ["-c:v", "copy"]

        # Audio
        if transcode_vlc or audio_bitrate:
            cmd += ["-c:a", "aac"]
            cmd += ["-b:a", audio_bitrate if audio_bitrate else "128k"]
        else:
            cmd += ["-c:a", "copy"]

        cmd += ["-f", "flv", output]
    else:
        # Simple copy (no re-encode)
        cmd = ["ffmpeg", "-i", input_stream, "-c", "copy", "-f", "flv", output]

    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# ==========================
# MAIN STREAMING LOGIC
# ==========================
processes = []

if stream:
    if twitch:
        processes.append(start_ffmpeg(twitch_url, video_bitrate=twitch_video_bitrate, audio_bitrate=twitch_audio_bitrate))
        print("Twitch streaming enabled.")
    else:
        print("Twitch streaming disabled.")

    if kick:
        processes.append(start_ffmpeg(kick_url, video_bitrate=kick_video_bitrate, audio_bitrate=kick_audio_bitrate))
        print("Kick streaming enabled.")
    else:
        print("Kick streaming disabled.")

    if vlc:
        processes.append(start_ffmpeg(vlc_url, transcode_vlc=True, video_bitrate=vlc_video_bitrate, audio_bitrate=vlc_audio_bitrate))
        print("VLC streaming enabled (H.264/AAC).")
    else:
        print("VLC streaming disabled.")

    if not processes:
        print("No outputs enabled. Exiting.")
        sys.exit(0)

    print("Streaming started...")

    # Function to stop streams cleanly
    def stop_stream(signal_received, frame):
        print("\nStopping streams...")
        for p in processes:
            p.send_signal(signal.SIGINT)
            p.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop_stream)

    # Print FFmpeg output live
    try:
        while True:
            for p in processes:
                line = p.stdout.readline()
                if line:
                    print(line.decode('utf-8'), end='')
    except KeyboardInterrupt:
        stop_stream(None, None)

else:
    print("Streaming is disabled. Set stream = True to start streaming.")
