# Project Hail Mary: Eridian Translator

by Hernan Le

---

I love Project Hail Mary

<details open> <summary><h2>About</h2></summary>

In the book, no AI was used for core functions on the Hail Mary, as it was deemed too risky. Although it's possible the mission could've loaded some model onto the massive data drives aboard the Hail Mary, I like to think that Grace wrote a translator script using classical algorithms. After all, he did say it was a simple script.

**This was not a simple script.**

Not to me, at least. Then again, Grace is the story's protagonist.

Anyways, I was super excited for the movie, and I began this project after spring break in March in hopes that I would finish by the time the movie released. 

**I did not.** 

Work got busy for a while, but I returned to this project in June and made some notable changes.

- Using dynamic time warping (DTW) instead of audio fingerprinting to account for faster/slower audio.
- Decided to leave pitch/octave fluctuation (indicative of Rocky's tone/emotion) out of the scope. 
- Assume Rocky knows to slow his speech down enough so that there is a brief gap of silence between his words. This eliminated the dreaded problem of parsing words in real time.

This was a super fun project to work on, and it was very satisfying to solve one problem after another to bring this program to life. 

</details>

<details open> <summary> <h2>How to use: </h2></summary>

```eridian_translator.py```, takes in audio and matches recording to words in an AudioDictionary, printing the word to the terminal. If no match is found, "???" will be printed. 

When encountering a "???", assign a word to the audio by entering the word enclosed by angle brackets.

For example: "\<word\>"

The program will continue parsing words, which may visually conflict with user input, but upon submitting the word, only the user inputted text will be processed.

To skip assigning a word to audio, simply press Enter. A reminder of how many "???" there are left to be assigned a word will be printed.

Without angle brackets, the program will also skip assigning a word to audio.

Avoid pressing Enter multiple times for a single "???" because doing so will actually queue input for future "???". 

For instance, pressing Enter 5 times will queue up inputs (empty inputs: "") for the next 5 "???" and will automatically apply those inputs as the "???" arrive.

</details>

## Notes
