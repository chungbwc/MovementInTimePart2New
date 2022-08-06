# MovementInTimePart2New
This is the repository for the new version of the Movement in Time, Part 2 artwork, to be exhibited in the Hong Kong Museum of Art in late 2022. The software is rewritten from Processing to Python.

The project MoveTrain001 performs machine learning training of the 1000 cursive style Chinese characters. The current version will separate the writing into 10 frames with a 3 x 3 grid for each frame. The training and matching are done with the [scikit-learn](https://scikit-learn.org/stable/) library for Python.

The project MOA005 is the non-interactive version of the artwork, i.e. the [original version](http://www.magicandlove.com/blog/2021/03/27/movement-in-time-part-2-2016/) with slight changes in the visualisation. This version will visualise 2 martial art film fighting sequences, The Burning of the Red Lotus Monastery 1963 and the Dragon Inn 1967.


![Non-interactive version](https://img.youtube.com/vi/iMfCi-dp9dk/mqdefault.jpg)

The project MoveFlow018 is the new interactive version of the artwork that interprets the live movement of the audience and converts it into the writing of the cursive style Chinese calligraphy, with the database generated from MoveTrain001. The software uses the [MediaPipe](https://google.github.io/mediapipe/solutions/pose.html) for the movement tracking.


![Interactive version](https://img.youtube.com/vi/00jUlfcGC1E/mqdefault.jpg)
