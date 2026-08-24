import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive.file"
]


def get_credentials():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(
                host="localhost",
                port=8081,
                open_browser=True
            )

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def create_google_quiz(
    questions,
    title="AI Generated Quiz"
):
    creds = get_credentials()

    forms_service = build(
        "forms",
        "v1",
        credentials=creds
    )

    form = forms_service.forms().create(
        body={
            "info": {
                "title": title
            }
        }
    ).execute()

    form_id = form["formId"]

    requests = []

    index = 0


    # NAME
    requests.append(
        {
            "createItem": {
                "item": {
                    "title": "Name",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {}
                        }
                    }
                },
                "location": {
                    "index": index
                }
            }
        }
    )

    index += 1


    # REGISTER NUMBER
    requests.append(
        {
            "createItem": {
                "item": {
                    "title": "Register Number",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {}
                        }
                    }
                },
                "location": {
                    "index": index
                }
            }
        }
    )

    index += 1


    # ENROLLMENT NUMBER
    requests.append(
        {
            "createItem": {
                "item": {
                    "title": "Enrollment Number",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {}
                        }
                    }
                },
                "location": {
                    "index": index
                }
            }
        }
    )

    index += 1


    # YEAR
    requests.append(
        {
            "createItem": {
                "item": {
                    "title": "Year",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "DROP_DOWN",
                                "options": [
                                    {"value": "I"},
                                    {"value": "II"},
                                    {"value": "III"},
                                    {"value": "IV"}
                                ],
                                "shuffle": False
                            }
                        }
                    }
                },
                "location": {
                    "index": index
                }
            }
        }
    )

    index += 1


    # SECTION
    requests.append(
        {
            "createItem": {
                "item": {
                    "title": "Section",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "DROP_DOWN",
                                "options": [
                                    {"value": "A"},
                                    {"value": "B"},
                                    {"value": "C"}
                                ],
                                "shuffle": False
                            }
                        }
                    }
                },
                "location": {
                    "index": index
                }
            }
        }
    )

    index += 1


    # MAKE FORM A QUIZ
    forms_service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [
                {
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {
                                "isQuiz": True
                            }
                        },
                        "updateMask": "quizSettings.isQuiz"
                    }
                }
            ]
        }
    ).execute()


    # ADD AI GENERATED QUESTIONS
    for question in questions:

        options = question["options"]

        correct_index = question["correct_answer"]

        correct_answer = options[correct_index]

        requests.append(
            {
                "createItem": {
                    "item": {
                        "title": question["question"],
                        "questionItem": {
                            "question": {
                                "required": True,
                                "grading": {
                                    "pointValue": 1,
                                    "correctAnswers": {
                                        "answers": [
                                            {
                                                "value": correct_answer
                                            }
                                        ]
                                    }
                                },
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [
                                        {
                                            "value": option
                                        }
                                        for option in options
                                    ],
                                    "shuffle": False
                                }
                            }
                        }
                    },
                    "location": {
                        "index": index
                    }
                }
            }
        )

        index += 1


    # ADD ALL FORM ITEMS
    forms_service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": requests
        }
    ).execute()


    form_url = (
        f"https://docs.google.com/forms/d/"
        f"{form_id}/edit"
    )

    return form_url