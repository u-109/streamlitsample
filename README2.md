# Group Vocabulary App — Streamlit Version

> **Project Status:** The HTML version has been developed with 3,000 vocabulary words. Streamlit conversion and deployment are pending.

## 1. Group Information

- **Group:** G2
- **Members (roles):**
  - [Name] — [Role]
  - [Name] — [Role]
  - [Name] — [Role]
- **Project Repository:** https://github.com/u-109/streamlitsample

## 2. Target Learners

- Korean second-year high school students (고2).
- Students with different English vocabulary proficiency levels.
- Learners who want to study vocabulary at an appropriate difficulty level and develop consistent study habits.

## 3. Learning Goals

Our application aims to help students:

1. Identify their vocabulary proficiency through a placement test and begin studying at one of three levels.
2. Learn English vocabulary through meanings, spelling, example sentences, word families, and variations when available.
3. Improve vocabulary retention by reviewing missed words through different question types.
4. Develop consistent learning habits by tracking their weekly study progress.

## 4. What We Updated

We improved the original vocabulary learning application to provide a more personalized and engaging learning experience.

### Vocabulary and Learning System
- Expanded the vocabulary database from 20 to **3,000 words**.
- Classified vocabulary into three difficulty levels based on the original vocabulary dataset.
- Added a placement test to determine each learner's starting level.
- Added a tutorial for first-time users.
- Removed the original set-based study system and introduced level-based vocabulary learning.

### Learning Features
- Preserved the original flashcard and fill-in-the-blank quiz features.
- Added a retry function that allows students to review missed words using a different question type.
- Added a weekly study streak to encourage consistent learning.
- Added a landing page that organizes the main learning features.

### Design and Interaction
- Redesigned the interface with brighter colors and a more learner-friendly layout.
- Improved navigation for both desktop and mobile users.
- Added interactive sound effects and a mute option.
- Added local storage support for learning progress and settings.

### Technical Development
- Integrated the expanded vocabulary dataset into the HTML application.
- Preserved the original vocabulary learning functions while modifying the navigation and level system.
- Prepared the vocabulary data for future integration into a Streamlit application.

## 5. Main Features

### 1. Placement Test

When students open the application for the first time, they complete a short placement test.

- The test contains **9 multiple-choice questions**.
- Each vocabulary level contributes three questions.
- Students choose the correct Korean meaning of an English word.
- The results determine whether students begin at Level 1, Level 2, or Level 3.
- Students can retake the placement test from the landing page.

The test helps students begin learning at a level appropriate to their vocabulary knowledge.

### 2. Flashcards and Vocabulary Quiz

The application provides two main vocabulary learning activities.

**Flashcards**
- Display English words and their Korean meanings.
- Provide example sentences to help students understand vocabulary usage.
- Show word families and spelling variations when available.
- Allow students to listen to word pronunciation.
- Allow students to indicate whether they know a word.

**Vocabulary Quiz**
- Provides 10 questions per quiz session.
- Requires students to recall and type the correct English word.
- Includes sentence-based questions from the original application.
- Uses Korean meanings as clues for vocabulary added from the expanded dataset.
- Provides immediate feedback and correct answers.

These activities help learners practice vocabulary recognition, spelling, and recall.

### 3. Review and Retry with a Different Question Type

The application automatically collects words that students answer incorrectly or mark as unfamiliar.

- Missed words appear in a separate Review tab.
- Students receive immediate feedback after answering.
- Students can retry missed words using another question type.
- Words remain in the review list until students answer correctly during the retry.

This feature encourages students to revisit difficult vocabulary rather than simply memorizing answers to repeated questions.

### 4. Weekly Study Streak

The weekly study streak helps students monitor their study habits.

- Displays study activity from Monday to Sunday.
- Marks the days on which students complete a quiz session.
- Shows the number of consecutive study days.
- Saves study records locally so they can remain available after refreshing the page.

This feature is designed to motivate students to practice vocabulary regularly.

### 5. Landing Page and Tutorial

The landing page provides easy access to the application's main functions.

- Flashcards
- Vocabulary Quiz
- Review
- Placement Test
- Weekly Study Progress

First-time users are guided through a short tutorial before taking the placement test.

After completing the test, students can access the learning activities through the landing page or the bottom navigation menu.

## 6. Vocabulary Data

### 6.1 Vocabulary Database

We expanded the original vocabulary database using the provided **Voca_3000.csv** dataset.

The original CSV includes English words, Korean meanings, vocabulary difficulty classifications, and variation information.

We used this dataset to create an expanded vocabulary file containing **3,000 English words**.

The vocabulary is divided into three levels based on the difficulty classifications provided in the original CSV file.

| Original Classification | App Level | Number of Words |
|---|---|---:|
| Elementary | Level 1 — Basic | 800 |
| MidHigh | Level 2 — Intermediate | 1,200 |
| Extended | Level 3 — Advanced | 1,000 |
| **Total** | | **3,000** |

This classification allows learners to study vocabulary according to their proficiency level.

### 6.2 CSV Data Structure

The expanded vocabulary file is named `Voca_3000_with_examples.csv`.

It contains the following columns:

| Column | Description | Use in the Application |
|---|---|---|
| Word | English vocabulary item | Flashcards, quizzes, and placement test |
| Word-family | Related words | Flashcard information when available |
| Variation | Related or alternative word forms | Flashcard information |
| Level | Vocabulary difficulty (1–3) | Placement test and level-based learning |
| Meaning (Korean) | Korean meaning of the word | Flashcards, quizzes, and feedback |
| Example sentence | English example sentence | Flashcard examples |
| Example source | Origin or review status of the example | Identifying examples that need review |

The Word-family column is currently empty in the expanded CSV. However, the application preserves available word-family information from the original 20-word dataset.

### 6.3 How We Used the Vocabulary Data

The CSV file serves as the main source of vocabulary information for our application.

**First, we used the Level column to organize vocabulary learning.**

The original difficulty categories were converted into three numerical levels.

After completing the placement test, students are assigned a starting level. The application then selects vocabulary from the corresponding level.

**Second, we used the Word and Meaning (Korean) columns to create learning activities.**

These columns provide the information needed for flashcards, vocabulary questions, and answer checking.

The placement test also uses vocabulary meanings to generate multiple-choice questions.

**Third, we used the Variation column to provide additional vocabulary information.**

When variation information is available, students can view related word forms on their flashcards.

The application also preserves the word-family and spelling information from the original vocabulary dataset.

**Fourth, we added an Example sentence column to support contextual learning.**

Each of the 3,000 vocabulary entries has an English example sentence.

These sentences are displayed on flashcards to help students encounter vocabulary in context.

The original application's sentence-based quiz questions were preserved. For most newly added vocabulary items, the current quiz uses Korean meanings as clues for English word recall.

Some automatically generated example sentences still require teacher review before classroom use.

**Finally, we integrated the vocabulary data into the HTML application.**

The expanded CSV data was converted into a JavaScript vocabulary array embedded in the HTML file.

This allows the current application to operate locally without requiring an internet connection or external data files.

For the planned Streamlit version, the CSV can be loaded directly using pandas.

### 6.4 Vocabulary Data File

**File:** `Voca_3000_with_examples.csv`

**GitHub Link:** [Add the CSV file URL after uploading it to the repository.]

The vocabulary database can be expanded or revised by updating the CSV file and regenerating the vocabulary data used by the HTML application.

## 7. What We Learned Through This Group Activity

Through this project, we learned that organizing vocabulary data is an important part of developing an educational application.

By using a structured vocabulary dataset, we were able to expand the application from 20 words to 3,000 words and organize the vocabulary into three difficulty levels.

We also learned that effective vocabulary learning involves more than memorizing English words and their Korean meanings. Features such as placement tests, contextual examples, immediate feedback, and repeated practice can help create a more personalized learning experience.

During development, we considered how students would interact with the application. We focused on making the interface easy to understand, providing useful feedback, and encouraging students to continue studying even after making mistakes.

We also recognized the importance of checking vocabulary data and example sentences carefully, especially when automatically generated content is used for educational purposes.

Overall, this project helped us understand how vocabulary data, learning activities, and interface design can work together to support students' vocabulary learning.

## 8. Streamlit App

**Streamlit App Link:** [Add the deployed Streamlit URL.]