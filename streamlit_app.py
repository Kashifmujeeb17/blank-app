# file: mini_ipip_streamlit.py

import streamlit as st
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime
import os
import random

SAVE_PATH = "mini_ipip_responses.csv"


def get_questions() -> List[Dict]:
    return [
        {"text": "I am the life of the party.", "trait": "E", "reverse": False},
        {"text": "I sympathize with others' feelings.", "trait": "A", "reverse": False},
        {"text": "I get chores done right away.", "trait": "C", "reverse": False},
        {"text": "I have frequent mood swings.", "trait": "N", "reverse": False},
        {"text": "I have a vivid imagination.", "trait": "O", "reverse": False},
        {"text": "I don't talk a lot.", "trait": "E", "reverse": True},
        {"text": "I am not interested in other people's problems.", "trait": "A", "reverse": True},
        {"text": "I often forget to put things back in their proper place.", "trait": "C", "reverse": True},
        {"text": "I am relaxed most of the time.", "trait": "N", "reverse": True},
        {"text": "I am not interested in abstract ideas.", "trait": "O", "reverse": True},
        {"text": "I talk to a lot of different people at parties.", "trait": "E", "reverse": False},
        {"text": "I feel others' emotions.", "trait": "A", "reverse": False},
        {"text": "I like order.", "trait": "C", "reverse": False},
        {"text": "I get upset easily.", "trait": "N", "reverse": False},
        {"text": "I have difficulty understanding abstract ideas.", "trait": "O", "reverse": True},
        {"text": "I keep in the background.", "trait": "E", "reverse": True},
        {"text": "I am not really interested in others.", "trait": "A", "reverse": True},
        {"text": "I make a mess of things.", "trait": "C", "reverse": True},
        {"text": "I seldom feel blue.", "trait": "N", "reverse": True},
        {"text": "I do not have a good imagination.", "trait": "O", "reverse": True},
    ]


def get_demo_test() -> List[Dict]:
    return [
        {"text": "What is 7 + 5?", "answer": 12},
        {"text": "What is 15 - 6?", "answer": 9},
        {"text": "What is 3 x 4?", "answer": 12},
        {"text": "What is 16 ÷ 4?", "answer": 4},
        {"text": "If a pen costs 10 and a notebook costs 20, how much for both?", "answer": 30}
    ]


def calculate_scores(answers: List[Tuple[str, int]]) -> Dict[str, int]:
    trait_scores = {trait: 0 for trait in "OCEAN"}
    for trait, score in answers:
        if trait in trait_scores:
            trait_scores[trait] += score
    return trait_scores


def score_to_label(score: int) -> str:
    if score >= 16:
        return "Very High"
    elif score >= 13:
        return "High"
    elif score >= 9:
        return "Average"
    elif score >= 6:
        return "Low"
    else:
        return "Very Low"


def get_trait_summary(trait: str, label: str) -> str:
    summaries = {
        "O": "Openness: creativity, abstract thinking, curiosity.",
        "C": "Conscientiousness: organization, diligence, reliability.",
        "E": "Extraversion: sociability, enthusiasm, assertiveness.",
        "A": "Agreeableness: compassion, cooperation, kindness.",
        "N": "Neuroticism: emotional instability, anxiety, moodiness."
    }
    return summaries.get(trait, "") + f" Level: {label}"


view_mode = st.radio("Select view", ["Take the Test", "Admin Panel"])

if view_mode == "Admin Panel":
    st.title("🔐 Admin Panel")
    admin_pass = st.text_input("Enter Admin Password:", type="password")
    if admin_pass == "admin123":
        demo_threshold = st.number_input("Set Demo Score Threshold", min_value=0, max_value=5, value=3)
        personality_weight = st.slider("Personality Weight (%)", 0, 100, 50)
        demo_weight = 100 - personality_weight

        trait_thresholds = {}
        st.subheader("Set Thresholds for All Traits")
        for trait in "OCEAN":
            trait_thresholds[trait] = st.number_input(f"Minimum {trait} Score", min_value=0, max_value=20, value=12,
                                                      key=f"threshold_{trait}")

        st.subheader("📄 Job Description & Required Skills")
        jd_text = st.text_area("Paste Job Description")
        jd_skills = st.text_input("Key Skills (comma-separated)")

        if os.path.exists(SAVE_PATH):
            new_df = pd.read_csv(SAVE_PATH)

            trait_map = {
                "O": "Openness",
                "C": "Conscientiousness",
                "E": "Extraversion",
                "A": "Agreeableness",
                "N": "Neuroticism"
            }

            def compute_combined_score(row):
                failed_traits = [t for t in trait_map if row[trait_map[t]] < trait_thresholds[t]]
                personality_score = sum([row[trait_map[t]] >= trait_thresholds[t] for t in trait_map]) / 5
                demo_score = row["Demo Score"] / 5
                combined = (personality_score * personality_weight + demo_score * demo_weight) / 100
                reasons = ", ".join(failed_traits) if failed_traits else "-"
                return pd.Series([combined, reasons])

            new_df[["Combined Score", "Failed Traits"]] = new_df.apply(compute_combined_score, axis=1)
            new_df["Recommendation"] = new_df["Combined Score"].apply(
                lambda x: "Recommend" if x >= 0.5 else "Not Recommend")

            st.download_button("Download Results CSV", new_df.to_csv(index=False).encode("utf-8"), "results.csv",
                               "text/csv")
            st.dataframe(new_df, use_container_width=True)

            st.subheader("🥇 Dominant Traits Table")

            def extract_top_2(row):
                traits = row[["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]]
                top_traits = traits.sort_values(ascending=False).head(2)
                return ", ".join(top_traits.index)

            new_df["Top 2 Traits"] = new_df.apply(extract_top_2, axis=1)
            st.dataframe(new_df[
                ["Recommendation", "Combined Score", "Failed Traits", "Timestamp", "Name", "Final Trait",
                 "Top 2 Traits", "Demo Score"]])
        else:
            st.info("No submissions yet.")
    elif admin_pass:
        st.warning("Invalid password.")

elif view_mode == "Take the Test":
    st.title("Mini-IPIP Personality + Demo Assessment")
    name = st.text_input("Enter your name (optional):")
    uploaded_cv = st.file_uploader("Upload your CV (PDF only)", type=["pdf"])

    questions = get_questions()
    random.shuffle(questions)
    question_order = [q['text'] for q in questions]
    demo_questions = get_demo_test()

    responses = []
    demo_correct = 0

    with st.form("assessment_form"):
        st.subheader("Personality Questions")

        for i, q in enumerate(questions):
            key = f"q{i + 1}"
            default = st.session_state.get(key, 3)
            rating = st.slider(label=f"S.No {i + 1}: {q['text']}", min_value=1, max_value=5, value=default, key=key)
            rating = 6 - rating if q["reverse"] else rating
            responses.append((q["trait"], rating))

        submitted = st.form_submit_button("Continue to Demo Assessment")

    if submitted:
        st.session_state.finished_personality = True

    if st.session_state.get("finished_personality") and not st.session_state.get("demo_submitted"):
        st.subheader("Demo Test")
        for idx, question in enumerate(demo_questions):
            user_answer = st.number_input(question["text"], step=1, key=f"demo_{idx}")
            if user_answer == question["answer"]:
                demo_correct += 1

        if st.button("Submit Assessment"):
            st.session_state.demo_submitted = True

            scores = calculate_scores(responses)

            row = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Name": name if name else "Anonymous",
                "Openness": scores["O"],
                "Conscientiousness": scores["C"],
                "Extraversion": scores["E"],
                "Agreeableness": scores["A"],
                "Neuroticism": scores["N"],
                "Final Trait": score_to_label(scores[max(scores, key=scores.get)]),
                "Demo Score": demo_correct,
                "Question Order": " || ".join(question_order)
            }

            if uploaded_cv is not None:
                cv_save_path = f"cv_uploads/{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                os.makedirs("cv_uploads", exist_ok=True)
                with open(cv_save_path, "wb") as f:
                    f.write(uploaded_cv.read())
                row["CV File"] = cv_save_path

            if os.path.exists(SAVE_PATH):
                existing = pd.read_csv(SAVE_PATH)
                new_df = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
            else:
                new_df = pd.DataFrame([row])

            new_df.to_csv(SAVE_PATH, index=False)
            st.success("✅ Your responses have been submitted. Thank you!")
