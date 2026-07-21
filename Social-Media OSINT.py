import tkinter as tk
from tkinter import Entry, Button, Label
import webbrowser

root=tk.Tk()
root.title("SAVE TOO MAY CLICKS")
root.configure(bg="#48b7cb")
def youtube_search():
    query=entry.get()
    url=f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)

def google_search():
    query=entry.get()
    url=f"https://www.google.com/search?q={query}"
    webbrowser.open(url)

def instagram_search():
    usernmae=entry.get()
    url=f"https://www.instagram.com/{usernmae}/"
    webbrowser.open(url)


def facebook_search():
    username=entry.get()
    url=f"https://www.facebook.com/{username}/"
    webbrowser.open(url)

def tiktok_search():
    username=entry.get()    
    url=f"https://www.tiktok.com/@{username}/"
    webbrowser.open(url)
Label(root, text="SAVE TOO MANY CLICKS:").pack(pady=10)
entry=Entry(root, width=50)
entry.pack(pady=5)
Button(root, text="Search On YouTube", command=youtube_search).pack(pady=5)
Button(root, text="Search On Google", command=google_search).pack(pady=5)
Button(root, text="Search On Instagram", command=instagram_search).pack(pady=5)
Button(root, text="Search On Facebook", command=facebook_search).pack(pady=5)
Button(root, text="Search On TikTok", command=tiktok_search).pack(pady=5)

root.mainloop()
