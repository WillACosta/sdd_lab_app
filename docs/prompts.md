## Initial prompt

I want to create a read-it-later app to store my articles URLs, before going to the implementation we
need the implementation options we have to achieve it.

The app should feature:

- A simple form to add a website URL with a button or shortcut command to add it
- A page to list all stored URLs

The app souldn't have login yet, it needs to be simple, we can store the data in a simple JSON
database, as it's only text based content. When a new item is added we need to extract its metadata
and store it in the db, the user should receive a message as feedback to inform if the content was
saved or not.

The stack: Streamlit for the frontend, python for the backend (a simple server just to separate
frontxback domains).

You should create a file named: `spec.md` that needs to describe the implementation, follow the
concepts of "Spec-Driven Development", the file should use the "MUST", "SHOULD" and "MAY" keywords as
stated at RFC2119 when describing requirements.

## Acting as Reviwer

Read the `spec.md` and act as a REVIEWER, you should analyze it and give your opinion about its desciption, is it consistent? Easy to understand by both humans and AIs?
