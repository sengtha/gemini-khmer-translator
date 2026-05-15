# 🇰🇭 Gemini Khmer Video Translator

An open-source, AI-powered pipeline that automatically translates English video content into high-quality Khmer. Built with a "Vibe Coding" philosophy for rapid, natural-language-driven prototyping, this tool leverages Google's cutting-edge Gemini Multimodal APIs to generate both studio-quality voice dubs and perfectly synced WebVTT subtitles.

## ✨ Features

* **Native Khmer TTS:** Uses Gemini 3.1 Flash TTS (with custom directorial prompts) to generate expressive, natural-sounding Cambodian voices (e.g., `Aoede`, `Erinome`, `Enceladus`).
* **Smart Subtitling:** Generates strict, timeline-accurate `.vtt` WebVTT subtitle files natively supported by HTML5 web browsers.
* **Context-Aware Translation:** Uses Gemini 2.5 Flash's multimodal capabilities to listen to the video's audio directly, rather than relying on error-prone intermediary transcripts.
* **Built-in Web Player:** Automatically generates an `index.html` file to instantly preview your translated video and subtitles on any mobile or desktop browser.

## 🚀 Prerequisites

* Python 3.10+
* A Google Gemini API Key (Accessible via Google AI Studio)
* FFmpeg (required by MoviePy for video processing)

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/gemini-khmer-translator.git](https://github.com/yourusername/gemini-khmer-translator.git)
   cd gemini-khmer-translator
