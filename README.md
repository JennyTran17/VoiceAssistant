# VoiceAssistant

A prototype voice assistant built to demonstrate speech interaction and template-based responses, with a modular design for future expansion into more advanced features.

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Architecture & Workflow](#architecture--workflow)
* [Code Structure](#code-structure)
* [Dependencies](#dependencies)
* [Setup & Usage](#setup--usage)
* [Extending the Assistant](#extending-the-assistant)
* [Acknowledgements & License](#acknowledgements--license)

---

## Overview

VoiceAssistant is a simple voice interaction system that takes in spoken input, matches it against a limited set of predefined templates stored in a local database, and returns a spoken response. It is structured as a prototype / base layer, ready to be extended with richer knowledge sources, contextual understanding, and external integrations.

The goal is to provide a clean starting point for exploring speech recognition, template matching, and text-to-speech flows, while keeping things modular so that future enhancements (like NLP, memory, APIs) are easier to plug in.

---

## Features (Current)

* Accepts voice input (microphone → speech recognition)
* Converts recognized text into a response via template matching
* Speaks the response using text-to-speech
* Local, limited database of templates / triggers
* Clean modular separation between input, logic, and output

---

## Architecture & Workflow

Here’s the high-level flow:

1. **Audio capture & Speech Recognition**
   The system listens on the microphone, captures audio, and uses a speech recognition library or API to convert spoken words into text.

2. **Intent / Template Matching**
   The recognized text is compared with entries in the internal database (e.g. JSON, dictionary) to find the best matching response template. Matching is currently simple (keywords, exact triggers).

3. **Response Selection & Generation**
   Once a template is selected, if it has placeholders or dynamic parts, they can be filled in. Right now responses are mostly static template text.

4. **Text-to-Speech & Audio Output**
   The response text is passed to a TTS component which synthesizes speech and plays it back to the user.

5. **Database / Knowledge Store**
   A local store (JSON / data file) maintains the mappings between triggers/commands and response templates. This store is intended to grow and be replaced or supplemented by more sophisticated stores later.

---

## Dependencies

Here are typical dependencies (based on `requirements.txt`):

* `speechrecognition` (or equivalent for speech → text)
* `pyttsx3`, `gTTS`, or another TTS library
* `pyaudio` or `sounddevice` for microphone access
* Standard libraries (json, os, etc.)

---

## Setup & Usage

### Prerequisites

* Python 3.x installed
* Microphone and audio output device properly working
* (Optional) Any API keys if integrate external services later

### Installation & Running

```bash
git clone https://github.com/JennyTran17/VoiceAssistant.git  
cd VoiceAssistant  
pip install -r requirements.txt  
python app.py  
```

Once running, speak a supported command or phrase. The assistant listens, matches, then replies via voice.

---

## Extending the Assistant

* **Expand the template database** — Add more commands, more varied responses.
* **Improve matching logic** — Swap exact matching for fuzzy matching, regex, or a small intent classification model.
* **Add context / memory** — Maintain conversation state, reference previous queries.
* **Integrate external APIs** — Weather, news, calendar, web search, smart home, etc.
* **Use NLP / LLM backends** — For richer, generative responses rather than fixed templates.
* **Multilingual support** — Recognize and respond in different languages.
* **User profiles** — Adapt responses based on user preferences, profile, or history.
* **Dashboard / Admin UI** — For adding / editing templates, viewing logs, testing.

---

## Acknowledgements & License

* Thanks to open-source speech recognition and TTS libraries used in this project.

