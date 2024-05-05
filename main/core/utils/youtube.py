from pytube import YouTube


def get_video(url: str, filename: str) -> tuple[str, str, str]:
    yt = YouTube(url)

    video = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
    path = video.download(output_path='tmp', filename=filename)

    return path

