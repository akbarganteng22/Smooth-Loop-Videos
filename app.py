import streamlit as st
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from moviepy.video.fx.all import time_mirror
import tempfile
import os

# ---------------- Page config ----------------
st.set_page_config(page_title="Video Looper", page_icon="🎬", layout="centered")

# ---------------- Minimal dark theme (CSS) ----------------
dark_css = """
<style>
.stApp { background-color: #0f1117; color: #f0f0f0; }
h1, h2, h3, h4, h5, h6, .stMarkdown { color: #ffffff !important; }
[data-testid="stSidebar"] { background-color: #161a23; }
.stButton>button, .stDownloadButton>button {
  background:#2a2f3e; color:#f0f0f0; border:1px solid #444; border-radius:10px;
  padding:8px 16px; font-weight:600;
}
.stButton>button:hover, .stDownloadButton>button:hover { background:#3a4052; border-color:#666; }
.stNumberInput input, .stSelectbox, .stTextInput>div>div>input { background:#1e2230 !important; color:#fff !important; }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ---------------- Splash screen ----------------
splash_html = """
<style>
#splash-container {
    position: fixed; inset: 0; background: #111; display:flex;
    align-items:center; justify-content:center; z-index: 9999;
}
#splash-container img { width: 180px; animation: pulse 2s infinite; }
@keyframes pulse { 0%{transform:scale(1);opacity:1} 50%{transform:scale(1.1);opacity:.85} 100%{transform:scale(1);opacity:1} }
</style>
<div id="splash-container"><img src="logo.png" onerror="this.style.display='none'"></div>
<script>
  setTimeout(function(){
    var el = document.getElementById("splash-container");
    if (el) el.style.display = "none";
  }, 2000);
</script>
"""
st.markdown(splash_html, unsafe_allow_html=True)

# ---------------- Sidebar logo ----------------
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("🎬 Video Looping App")

# ---------------- Main UI ----------------
st.title("✨ Video Looping Tool")

uploaded_file = st.file_uploader("Upload video", type=["mp4", "mov", "mkv", "avi"])

col1, col2 = st.columns(2)
with col1:
    loop_mode = st.radio("Looping Mode", ["Normal", "Crossfade", "Ping-Pong"], horizontal=False)
with col2:
    res_option = st.selectbox("Output resolution", ["480p", "720p", "1080p"])

duration = st.number_input("Target duration (detik)", min_value=5, max_value=600, value=20, step=5)
process = st.button("🚀 Generate")

def resize_to_option(clip, res_option: str):
    target_h = 720
    if res_option == "480p": target_h = 480
    elif res_option == "720p": target_h = 720
    elif res_option == "1080p": target_h = 1080
    return clip.resize(height=target_h)

if process:
    if not uploaded_file:
        st.warning("Silakan upload video terlebih dahulu.")
        st.stop()

    with st.spinner("Memproses..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_in:
            tmp_in.write(uploaded_file.read())
            input_path = tmp_in.name

        try:
            clip = VideoFileClip(input_path)
            clip = resize_to_option(clip, res_option)

            if loop_mode == "Normal":
                repeat_count = int(duration // clip.duration) + 1
                looped = concatenate_videoclips([clip] * max(1, repeat_count), method="compose")

            elif loop_mode == "Crossfade":
                crossfade_duration = 1.0
                repeat_count = int(duration // clip.duration) + 1
                clips = [clip]
                for _ in range(max(0, repeat_count - 1)):
                    clips.append(clip.crossfadein(crossfade_duration))
                looped = concatenate_videoclips(clips, method="compose", padding=-crossfade_duration)

            else:  # Ping-Pong
                reverse_clip = time_mirror(clip)
                looped = concatenate_videoclips([clip, reverse_clip], method="compose")

            looped = looped.subclip(0, min(duration, looped.duration))

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_out:
                output_path = tmp_out.name

            fps_out = int(clip.fps) if clip.fps and clip.fps > 0 else 30
            looped.write_videofile(output_path, codec="libx264", audio=False, fps=fps_out)

            st.success("✅ Video berhasil diproses!")
            st.subheader("📺 Preview")
            st.video(output_path)

            with open(output_path, "rb") as f:
                st.download_button("⬇️ Download Video", f, file_name="looped_video.mp4")

        except Exception as e:
            st.error(f"Terjadi error saat pemrosesan: {e}")
        finally:
            try: clip.close()
            except: pass
            try: looped.close()
            except: pass
            try: os.remove(input_path)
            except: pass
