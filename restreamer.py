import subprocess
import signal
import sys

# ==========================
# SERVER/IP SETTINGS
# ==========================
server_ip = "your.ip.v.4.here"  # Local IP of this machine

# ==========================
# CONTROL FLAGS
# ==========================
stream = True
twitch = True
kick = True
vlc = True
vrchat = True

# ==========================
# INPUT STREAM FROM OBS
# ==========================
input_stream = f"rtmp://{server_ip}:1935/live/stream"

# ==========================
# OUTPUT STREAMS
# ==========================
twitch_url = "rtmp://live.twitch.tv/app/YOUR_TWITCH_KEY"
kick_url   = "rtmp://live.kick.com/app/YOUR_KICK_KEY"
vlc_url    = f"rtmp://{server_ip}:1935/live/vlc"
vrchat_url = f"rtsp://{server_ip}:8554/vrchat"  # FFmpeg RTSP server

# ==========================
# BITRATE SETTINGS
# ==========================
twitch_video_bitrate = "6000k"
twitch_audio_bitrate = "160k"

kick_video_bitrate = "6000k"
kick_audio_bitrate = "160k"

vlc_video_bitrate = "4000k"
vlc_audio_bitrate = "128k"

vrchat_video_bitrate = "4000k"
vrchat_audio_bitrate = "128k"

# ==========================
# FUNCTION TO START FFmpeg
# ==========================
def start_ffmpeg(output, transcode=False, video_bitrate=None, audio_bitrate=None, rtsp_server=False):
    cmd = ["ffmpeg", "-y", "-i", input_stream]

    # Video
    if transcode or video_bitrate or rtsp_server:
        cmd += ["-c:v", "libx264", "-preset", "veryfast"]
        if video_bitrate:
            cmd += ["-b:v", video_bitrate]
    else:
        cmd += ["-c:v", "copy"]

    # Audio
    if transcode or audio_bitrate or rtsp_server:
        cmd += ["-c:a", "aac", "-b:a", audio_bitrate if audio_bitrate else "128k"]
    else:
        cmd += ["-c:a", "copy"]

    # Output format
    if rtsp_server:
        cmd += ["-f", "rtsp", "-rtsp_flags", "listen", output]
    else:
        cmd += ["-f", "flv", output]

    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# ==========================
# MAIN STREAMING LOGIC
# ==========================
processes = []

if stream:
    if twitch:
        processes.append(start_ffmpeg(twitch_url, video_bitrate=twitch_video_bitrate, audio_bitrate=twitch_audio_bitrate))
        print("Twitch streaming enabled.")
    if kick:
        processes.append(start_ffmpeg(kick_url, video_bitrate=kick_video_bitrate, audio_bitrate=kick_audio_bitrate))
        print("Kick streaming enabled.")
    if vlc:
        processes.append(start_ffmpeg(vlc_url, transcode=True, video_bitrate=vlc_video_bitrate, audio_bitrate=vlc_audio_bitrate))
        print("VLC streaming enabled (H.264/AAC).")
    if vrchat:
        processes.append(start_ffmpeg(vrchat_url, transcode=True, video_bitrate=vrchat_video_bitrate, audio_bitrate=vrchat_audio_bitrate, rtsp_server=True))
        print("VRChat streaming enabled (RTSP H.264/AAC).")

    if not processes:
        print("No outputs enabled. Exiting.")
        sys.exit(0)

    # Handle Ctrl+C cleanly
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
