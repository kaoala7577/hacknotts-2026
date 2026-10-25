# inDEX - spaced repetition for sign languages

## Inspiration

Learning vocab for a foreign language in 2026 is easy. You add flashcards to Anki, review the cards, and repeat. Doing the same for a sign language is more complicated. You have to attend classes or follow a course and hope you memorise the signs eventually. Right now there is no way to continually practise signs you struggle to remember without manually tracking words and answer videos on a computer.

## What It Will Do

Anki for Sign Languages - any sign language! The app asks you to sign a phrase. You sign the phrase, and via the web cam recording, the app tells you whether your sign matched the correct sign or not. If you fail, the flashcard will be shown again until you pass.

## What It Does

Allows you to input reference videos and a final verification video to add a sign to the database, ready for flashcard and SRS implementation.

[inDEX Video Demo](https://drive.google.com/file/d/1dIO-Pi9xaRCdBLNFvIe0fnY_dHjQK9Y7/view?usp=sharing)

### Home Page

![home-screen-2](media/home-screen-2.png)

### Add Card Page

![review-screen-1](media/review-screen-1.png)

![review-screen-2](media/review-screen-2.png)

![verification-pass](media/verification-pass.png)

## How We Built It
- Frontend: PyQt6 - "home page and review screen"
- Backend: Python, Google MediaPipe, OpenCV, FastDTW - "handles processing the reference videos and comparing it to the answer video"
- Database: SQLlite - "stores flashcards - answer videos and phrases / words"
- Design: Microsoft Word, Qt Designer - "plan and design project"

## Challenges We Ran Into
- A lot of code online is written for PyQt5 but we are using PyQt6. We had issues with getting the QCamera widget to work and migrating to OpenCV
- Livestreaming the video to the backend meant that instead of processing an array of frames we had to process them one by one asynchronously which was a lot more difficult
- Since none of us had worked on the stack before, we weren't actually sure how PyQt6 would send signals or data to the backend, nor how MediaPipe's outputs would look
- Large scope of the project in 25 hours, especially with a new tech stack

## Accomplishments That We're Proud Of
- First time using the OpenCV and MediaPipe libraries
- First time tackling machine learning in a personal project
- First time using PyQt6 for frontend development
- First overnight hackathon for some members!

## What We Learned
- Sleep is important
- Should communicate our ideas more at the start so we don't have to do any U turns later

## What's Next
- Adding visualisation for the gesture recognition
- Adding the proper flashcard system rather than just the input system (all the code is there, just not implemented)
- Implementing the spaced repetition algorithm (SM2) so cards due for review are grabbed from the database
- Adding review buttons (Again, Hard, Good, Easy)
- Adding a collection screen with video previews
- Practical use and testing within UoN's Sign Language Society
