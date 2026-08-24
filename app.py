import streamlit as st

from ppt_reader import extract_text
from ai_generator import generate_mcqs
from google_forms import create_google_quiz


if "questions" not in st.session_state:
    st.session_state.questions = []

if "slides" not in st.session_state:
    st.session_state.slides = []

if "editing_question" not in st.session_state:
    st.session_state.editing_question = None

if "show_add_question" not in st.session_state:
    st.session_state.show_add_question = False

if "google_form_url" not in st.session_state:
    st.session_state.google_form_url = None


st.title("🤖 AI PowerPoint Quiz Generator")

st.write(
    "Upload a PowerPoint presentation and "
    "generate multiple-choice questions using AI."
)


uploaded_file = st.file_uploader(
    "Upload your PowerPoint",
    type=["pptx"]
)


if uploaded_file:

    st.success("PowerPoint uploaded successfully!")

    slides = extract_text(uploaded_file)

    st.session_state.slides = slides

    st.subheader("📖 Extracted PowerPoint Content")

    st.write(f"Total slides: {len(slides)}")

    for i, slide in enumerate(slides):

        with st.expander(f"Slide {i + 1}"):

            if slide:
                st.write(slide)

            else:
                st.write("No text detected on this slide.")


    st.divider()

    st.subheader("🧠 Generate MCQ Questions")

    number_of_questions = st.selectbox(
        "Number of questions",
        [5, 10, 15, 20, 30]
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard", "Mixed"]
    )


    if st.button("Generate MCQs"):

        combined_text = "\n\n".join(slides)

        if not combined_text.strip():

            st.error(
                "No readable text was found in the PowerPoint."
            )

        else:

            with st.spinner(
                "Gemini is generating questions..."
            ):

                result = generate_mcqs(
                    combined_text,
                    number_of_questions,
                    difficulty
                )

            if "error" in result:

                st.error(result["error"])

                st.write("Gemini response:")

                st.code(result["raw_response"])

            else:

                st.session_state.questions = result["questions"]

                st.session_state.editing_question = None

                st.session_state.google_form_url = None

                st.success(
                    f"{len(st.session_state.questions)} "
                    f"questions generated successfully!"
                )


if st.session_state.questions:

    st.divider()

    st.subheader("📝 Review Generated Questions")

    st.write(
        f"Total questions: "
        f"{len(st.session_state.questions)}"
    )


    if st.button(
        "➕ Add Question",
        use_container_width=True
    ):
        st.session_state.show_add_question = True
        st.rerun()


    if st.session_state.show_add_question:

        st.markdown("### ➕ Add New Question")

        new_question = st.text_area(
            "Question",
            key="new_question"
        )

        new_option_a = st.text_input(
            "Option A",
            key="new_option_a"
        )

        new_option_b = st.text_input(
            "Option B",
            key="new_option_b"
        )

        new_option_c = st.text_input(
            "Option C",
            key="new_option_c"
        )

        new_option_d = st.text_input(
            "Option D",
            key="new_option_d"
        )

        new_correct_answer = st.selectbox(
            "Correct Answer",
            ["A", "B", "C", "D"],
            key="new_correct_answer"
        )

        new_explanation = st.text_area(
            "Explanation",
            key="new_explanation"
        )

        new_difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Mixed"],
            key="new_difficulty"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "💾 Save New Question",
                use_container_width=True
            ):

                options = [
                    new_option_a,
                    new_option_b,
                    new_option_c,
                    new_option_d
                ]

                if not new_question.strip():

                    st.error("Question cannot be empty.")

                elif any(
                    not option.strip()
                    for option in options
                ):

                    st.error(
                        "All four options must contain text."
                    )

                else:

                    correct_index = [
                        "A",
                        "B",
                        "C",
                        "D"
                    ].index(
                        new_correct_answer
                    )

                    new_question_data = {
                        "question": new_question.strip(),
                        "options": [
                            option.strip()
                            for option in options
                        ],
                        "correct_answer": correct_index,
                        "difficulty": new_difficulty,
                        "explanation": new_explanation.strip()
                    }

                    st.session_state.questions.append(
                        new_question_data
                    )

                    st.session_state.show_add_question = False

                    st.session_state.google_form_url = None

                    st.rerun()


        with col2:

            if st.button(
                "❌ Cancel",
                key="cancel_add_question",
                use_container_width=True
            ):

                st.session_state.show_add_question = False

                st.rerun()


        st.divider()


    for i, question in enumerate(
        st.session_state.questions
    ):

        st.markdown(f"### Question {i + 1}")


        if st.session_state.editing_question == i:

            edited_question = st.text_area(
                "Question",
                value=question["question"],
                key=f"edit_question_{i}"
            )

            edited_options = []

            for option_index in range(4):

                edited_option = st.text_input(
                    f"Option {chr(65 + option_index)}",
                    value=question["options"][option_index],
                    key=f"edit_option_{i}_{option_index}"
                )

                edited_options.append(edited_option)


            answer_letters = ["A", "B", "C", "D"]

            current_correct_index = question["correct_answer"]

            edited_correct_answer = st.selectbox(
                "Correct Answer",
                answer_letters,
                index=current_correct_index,
                key=f"edit_correct_{i}"
            )


            edited_explanation = st.text_area(
                "Explanation",
                value=question.get("explanation", ""),
                key=f"edit_explanation_{i}"
            )


            difficulty_options = [
                "Easy",
                "Medium",
                "Hard",
                "Mixed"
            ]

            current_difficulty = question.get(
                "difficulty",
                "Mixed"
            )

            if current_difficulty not in difficulty_options:
                current_difficulty = "Mixed"

            difficulty_index = difficulty_options.index(
                current_difficulty
            )

            edited_difficulty = st.selectbox(
                "Difficulty",
                difficulty_options,
                index=difficulty_index,
                key=f"edit_difficulty_{i}"
            )


            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    "💾 Save Changes",
                    key=f"save_{i}",
                    use_container_width=True
                ):

                    if not edited_question.strip():

                        st.error(
                            "Question cannot be empty."
                        )

                    elif any(
                        not option.strip()
                        for option in edited_options
                    ):

                        st.error(
                            "All four options must contain text."
                        )

                    else:

                        correct_index = answer_letters.index(
                            edited_correct_answer
                        )

                        st.session_state.questions[i] = {
                            "question": edited_question.strip(),
                            "options": [
                                option.strip()
                                for option in edited_options
                            ],
                            "correct_answer": correct_index,
                            "difficulty": edited_difficulty,
                            "explanation": edited_explanation.strip()
                        }

                        st.session_state.editing_question = None

                        st.session_state.google_form_url = None

                        st.rerun()


            with col2:

                if st.button(
                    "❌ Cancel",
                    key=f"cancel_{i}",
                    use_container_width=True
                ):

                    st.session_state.editing_question = None

                    st.rerun()


        else:

            st.write(question["question"])

            options = question["options"]

            correct_index = question["correct_answer"]


            for option_number, option in enumerate(options):

                letter = chr(65 + option_number)

                st.write(
                    f"{letter}. {option}"
                )


            correct_letter = chr(65 + correct_index)

            st.success(
                f"Correct Answer: "
                f"{correct_letter}. "
                f"{options[correct_index]}"
            )

            st.info(
                f"Explanation: "
                f"{question.get('explanation', '')}"
            )

            st.caption(
                f"Difficulty: "
                f"{question.get('difficulty', 'Mixed')}"
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                if st.button(
                    "✏️ Edit",
                    key=f"edit_{i}",
                    use_container_width=True
                ):

                    st.session_state.editing_question = i

                    st.rerun()


            with col2:

                if st.button(
                    "🔄 Regenerate",
                    key=f"regenerate_{i}",
                    use_container_width=True
                ):

                    combined_text = "\n\n".join(
                        st.session_state.slides
                    )

                    current_difficulty = question.get(
                        "difficulty",
                        "Mixed"
                    )

                    with st.spinner(
                        f"Regenerating Question {i + 1}..."
                    ):

                        result = generate_mcqs(
                            combined_text,
                            1,
                            current_difficulty
                        )

                    if "error" in result:

                        st.error(result["error"])

                    elif (
                        "questions" in result
                        and len(result["questions"]) > 0
                    ):

                        new_question = result["questions"][0]

                        st.session_state.questions[i] = new_question

                        st.session_state.editing_question = None

                        st.session_state.google_form_url = None

                        st.rerun()

                    else:

                        st.error(
                            "Gemini did not generate a replacement question."
                        )


            with col3:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{i}",
                    use_container_width=True
                ):

                    st.session_state.questions.pop(i)

                    st.session_state.editing_question = None

                    st.session_state.google_form_url = None

                    st.rerun()


        st.divider()


    st.subheader("📋 Create Google Quiz")

    quiz_title = st.text_input(
        "Google Form Title",
        value="AI Generated Quiz"
    )


    if st.button(
        "🚀 Create Google Quiz",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Creating Google Quiz..."
            ):

                form_url = create_google_quiz(
                    st.session_state.questions,
                    quiz_title
                )

                st.session_state.google_form_url = form_url

            st.success(
                "Google Quiz created successfully!"
            )

        except Exception as error:

            st.error(
                f"Failed to create Google Quiz: {error}"
            )


    if st.session_state.google_form_url:

        st.success(
            "Your Google Quiz is ready."
        )

        st.link_button(
            "🔗 Open Google Quiz",
            st.session_state.google_form_url,
            use_container_width=True
        )