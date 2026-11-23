
from flask import Blueprint, jsonify, request

questionnaire_bp = Blueprint("questionnaire", __name__)

# Each question has four options: a, b, c, d.
# Personal and scenario questions measure preferences, not ability.
# Logical questions have objectively correct answers.

QUESTIONS = [
    # ---------------- PERSONAL INTERESTS: Q1-Q10 ----------------
    {
        "id": "q1", "section": "personal",
        "text": "Which school activity would you enjoy most?",
        "options": {
            "a": "Solving maths puzzles",
            "b": "Designing a poster or model",
            "c": "Helping classmates understand a topic",
            "d": "Doing a practical experiment"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "social", "d": "practical"
        }
    },
    {
        "id": "q2", "section": "personal",
        "text": "Which task sounds most interesting?",
        "options": {
            "a": "Finding patterns in data",
            "b": "Writing a story",
            "c": "Organising a group event",
            "d": "Learning how machines work"
        },
        "scores": {
            "a": "analytical", "b": "communication",
            "c": "organising", "d": "practical"
        }
    },
    {
        "id": "q3", "section": "personal",
        "text": "What would you prefer for a free weekend?",
        "options": {
            "a": "Learning a coding or technical skill",
            "b": "Making something artistic",
            "c": "Meeting friends or helping someone",
            "d": "Exploring nature"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "social", "d": "nature"
        }
    },
    {
        "id": "q4", "section": "personal",
        "text": "Which type of book or video attracts you most?",
        "options": {
            "a": "Science and technology",
            "b": "Art, design or storytelling",
            "c": "People, society and relationships",
            "d": "Wildlife and the environment"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "social", "d": "nature"
        }
    },
    {
        "id": "q5", "section": "personal",
        "text": "When learning something new, what do you prefer?",
        "options": {
            "a": "Understanding the logic behind it",
            "b": "Seeing a visual example",
            "c": "Discussing it with others",
            "d": "Trying it yourself"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "social", "d": "practical"
        }
    },
    {
        "id": "q6", "section": "personal",
        "text": "Which result would make you feel most satisfied?",
        "options": {
            "a": "Solving a difficult problem",
            "b": "Creating something original",
            "c": "Helping someone succeed",
            "d": "Building something that works"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "social", "d": "practical"
        }
    },
    {
        "id": "q7", "section": "personal",
        "text": "Which school project would you choose?",
        "options": {
            "a": "Analysing survey results",
            "b": "Making a short film or presentation",
            "c": "Researching a community problem",
            "d": "Building a working model"
        },
        "scores": {
            "a": "analytical", "b": "communication",
            "c": "social", "d": "practical"
        }
    },
    {
        "id": "q8", "section": "personal",
        "text": "Which work environment appeals to you most?",
        "options": {
            "a": "A quiet place to solve complex problems",
            "b": "A creative studio",
            "c": "A team-oriented environment",
            "d": "A workshop, lab or outdoor setting"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "social", "d": "practical"
        }
    },
    {
        "id": "q9", "section": "personal",
        "text": "Which activity would you like to improve at?",
        "options": {
            "a": "Reasoning and calculations",
            "b": "Drawing, designing or inventing",
            "c": "Speaking and explaining ideas",
            "d": "Hands-on experimentation"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "communication", "d": "practical"
        }
    },
    {
        "id": "q10", "section": "personal",
        "text": "Which real-world problem interests you most?",
        "options": {
            "a": "Making technology more useful",
            "b": "Making information easier to understand",
            "c": "Improving people's lives",
            "d": "Protecting the environment"
        },
        "scores": {
            "a": "analytical", "b": "communication",
            "c": "social", "d": "nature"
        }
    },

    # ---------------- LOGICAL REASONING: Q11-Q20 ----------------
    {
        "id": "q11", "section": "logical",
        "text": "Complete the series: 2, 6, 12, 20, 30, ?",
        "options": {
            "a": "36", "b": "40", "c": "42", "d": "44"
        },
        "correct": "c"
    },
    {
        "id": "q12", "section": "logical",
        "text": "What comes next: 3, 9, 27, 81, ?",
        "options": {
            "a": "162", "b": "189", "c": "243", "d": "324"
        },
        "correct": "c"
    },
    {
        "id": "q13", "section": "logical",
        "text": "All Bloops are Razzies. All Razzies are Lazzies. What must be true?",
        "options": {
            "a": "All Bloops are Lazzies",
            "b": "All Lazzies are Bloops",
            "c": "No Bloops are Lazzies",
            "d": "Some Razzies are not Bloops"
        },
        "correct": "a"
    },
    {
        "id": "q14", "section": "logical",
        "text": "A machine makes 5 items in 5 minutes. How many items can 10 identical machines make in 10 minutes?",
        "options": {
            "a": "10", "b": "20", "c": "50", "d": "100"
        },
        "correct": "d"
    },
    {
        "id": "q15", "section": "logical",
        "text": "Which number does not fit: 4, 9, 16, 20, 25?",
        "options": {
            "a": "9", "b": "16", "c": "20", "d": "25"
        },
        "correct": "c"
    },
    {
        "id": "q16", "section": "logical",
        "text": "A pen costs ₹10. A notebook costs ₹30. What do 2 pens and 3 notebooks cost?",
        "options": {
            "a": "₹80", "b": "₹100", "c": "₹110", "d": "₹120"
        },
        "correct": "c"
    },
    {
        "id": "q17", "section": "logical",
        "text": "If today is Monday, what day will it be 10 days later?",
        "options": {
            "a": "Wednesday", "b": "Thursday",
            "c": "Friday", "d": "Saturday"
        },
        "correct": "b"
    },
    {
        "id": "q18", "section": "logical",
        "text": "A class has 20 students. 12 like science, 10 like maths, and 5 like both. How many like at least one?",
        "options": {
            "a": "17", "b": "22", "c": "15", "d": "27"
        },
        "correct": "a"
    },
    {
        "id": "q19", "section": "logical",
        "text": "If A is taller than B and B is taller than C, who is the shortest?",
        "options": {
            "a": "A", "b": "B", "c": "C", "d": "Cannot be determined"
        },
        "correct": "c"
    },
    {
        "id": "q20", "section": "logical",
        "text": "A number is doubled and then 6 is added. The result is 20. What was the number?",
        "options": {
            "a": "5", "b": "6", "c": "7", "d": "8"
        },
        "correct": "c"
    },

    # ---------------- SITUATION-BASED: Q21-Q30 ----------------
    {
        "id": "q21", "section": "scenario",
        "text": "Your science experiment gives an unexpected result. What would you do first?",
        "options": {
            "a": "Check the procedure and data",
            "b": "Ask someone experienced for guidance",
            "c": "Try a different method",
            "d": "Discuss possible explanations with the team"
        },
        "scores": {
            "a": "analytical", "b": "seeking_guidance",
            "c": "experimental", "d": "collaborative"
        }
    },
    {
        "id": "q22", "section": "scenario",
        "text": "Two teammates disagree about an important decision. What would you do?",
        "options": {
            "a": "Compare the evidence for both ideas",
            "b": "Help them find a compromise",
            "c": "Suggest testing both ideas",
            "d": "Divide the problem into smaller tasks"
        },
        "scores": {
            "a": "analytical", "b": "collaborative",
            "c": "experimental", "d": "organised"
        }
    },
    {
        "id": "q23", "section": "scenario",
        "text": "You have a difficult assignment and only one day left. What is your first step?",
        "options": {
            "a": "Break it into smaller tasks and prioritise",
            "b": "Start with the hardest problem",
            "c": "Ask classmates to discuss difficult parts",
            "d": "Create a quick prototype or rough draft"
        },
        "scores": {
            "a": "organised", "b": "analytical",
            "c": "collaborative", "d": "experimental"
        }
    },
    {
        "id": "q24", "section": "scenario",
        "text": "A classmate is struggling to understand a topic. What would you do?",
        "options": {
            "a": "Explain it step by step",
            "b": "Draw a diagram or give an example",
            "c": "Ask what part is confusing them",
            "d": "Work through a practice problem together"
        },
        "scores": {
            "a": "communication", "b": "creative",
            "c": "empathetic", "d": "collaborative"
        }
    },
    {
        "id": "q25", "section": "scenario",
        "text": "Your first attempt at building an app does not work. What next?",
        "options": {
            "a": "Read the error and inspect the code",
            "b": "Try a small change and test again",
            "c": "Ask a teammate to review it",
            "d": "Review the plan and simplify the design"
        },
        "scores": {
            "a": "analytical", "b": "experimental",
            "c": "collaborative", "d": "organised"
        }
    },
    {
        "id": "q26", "section": "scenario",
        "text": "You are asked to present a topic you do not know well. What would you do?",
        "options": {
            "a": "Research reliable sources first",
            "b": "Use diagrams and examples to explain it",
            "c": "Ask the teacher what the audience needs to know",
            "d": "Prepare an outline and practise"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "communication", "d": "organised"
        }
    },
    {
        "id": "q27", "section": "scenario",
        "text": "Your team has many ideas but cannot choose one. What would you suggest?",
        "options": {
            "a": "Compare ideas against clear criteria",
            "b": "Vote after everyone explains their idea",
            "c": "Build a small version of the most promising ideas",
            "d": "Combine compatible ideas into one plan"
        },
        "scores": {
            "a": "analytical", "b": "collaborative",
            "c": "experimental", "d": "creative"
        }
    },
    {
        "id": "q28", "section": "scenario",
        "text": "You notice that a classmate is being left out of a group activity. What would you do?",
        "options": {
            "a": "Invite them to join the group",
            "b": "Ask them what activity they would enjoy",
            "c": "Suggest dividing tasks so everyone can contribute",
            "d": "Talk to the group about including everyone"
        },
        "scores": {
            "a": "empathetic", "b": "empathetic",
            "c": "organised", "d": "communication"
        }
    },
    {
        "id": "q29", "section": "scenario",
        "text": "You find two websites giving conflicting information for a project. What would you do?",
        "options": {
            "a": "Check the credibility and evidence of both",
            "b": "Look for a reliable third source",
            "c": "Discuss the difference with a teacher",
            "d": "Record the uncertainty before deciding"
        },
        "scores": {
            "a": "analytical", "b": "analytical",
            "c": "seeking_guidance", "d": "organised"
        }
    },
    {
        "id": "q30", "section": "scenario",
        "text": "You can choose one new project. Which approach appeals to you most?",
        "options": {
            "a": "Investigate a question using data",
            "b": "Design and create something original",
            "c": "Solve a problem affecting people",
            "d": "Test how a real-world system works"
        },
        "scores": {
            "a": "analytical", "b": "creative",
            "c": "social", "d": "experimental"
        }
    }
]



CAREER_GUIDES = {
    "analytical": [
        {"title": "Data Analyst", "why": "You often choose data, patterns, logic, or evidence-based tasks.",
         "skills": ["Python or spreadsheets", "Statistics", "Data visualisation"],
         "project": "Analyse a small public dataset and present three findings."},
        {"title": "Software Developer", "why": "You show interest in solving structured problems and understanding technology.",
         "skills": ["Programming fundamentals", "Debugging", "Problem solving"],
         "project": "Build a simple quiz app or task tracker."},
        {"title": "Researcher / Scientist", "why": "You may enjoy investigating questions and checking evidence.",
         "skills": ["Research methods", "Critical thinking", "Clear documentation"],
         "project": "Choose a question, compare reliable sources, and write a short evidence-based report."},
    ],
    "creative": [
        {"title": "UI/UX Designer", "why": "Your choices suggest interest in visual ideas, design, and improving experiences.",
         "skills": ["Design fundamentals", "Wireframing", "User research"],
         "project": "Redesign one screen of a school or everyday app and explain your choices."},
        {"title": "Graphic / Communication Designer", "why": "You may enjoy making information clear and visually engaging.",
         "skills": ["Visual hierarchy", "Typography", "Design tools"],
         "project": "Create a poster that explains a complex topic simply."},
        {"title": "Product Designer", "why": "This combines creativity with understanding a user's needs.",
         "skills": ["Problem framing", "Prototyping", "Feedback"],
         "project": "Sketch and test a prototype for a small everyday problem."},
    ],
    "social": [
        {"title": "Teacher / Learning Facilitator", "why": "Your answers indicate interest in helping people learn or succeed.",
         "skills": ["Communication", "Planning", "Explaining concepts"],
         "project": "Prepare a short lesson and ask a classmate for feedback."},
        {"title": "Psychology / Human Behaviour (exploration)", "why": "You may be interested in people, behaviour, and how they experience the world.",
         "skills": ["Listening", "Research literacy", "Ethical awareness"],
         "project": "Read an introductory, reliable article and summarise its key ideas."},
        {"title": "Community / Social Impact Work", "why": "You may enjoy understanding needs and helping improve people's lives.",
         "skills": ["Teamwork", "Communication", "Project planning"],
         "project": "Identify a local issue and propose a small, practical improvement."},
    ],
    "practical": [
        {"title": "Engineering / Prototyping", "why": "Your choices suggest you may enjoy hands-on tasks and making things work.",
         "skills": ["Maths and science foundations", "Testing", "Technical drawing or coding"],
         "project": "Build a simple working model and document what you changed during testing."},
        {"title": "Laboratory Technician (exploration)", "why": "You may like careful practical work, procedures, and experiments.",
         "skills": ["Following procedures", "Measurement", "Safety"],
         "project": "Design a safe classroom experiment and record observations."},
        {"title": "Robotics / IoT Explorer", "why": "This can combine practical building with technology and experimentation.",
         "skills": ["Basic electronics", "Programming", "Troubleshooting"],
         "project": "Prototype a simple sensor-based project using a beginner kit or simulator."},
    ],
    "nature": [
        {"title": "Environmental Scientist (exploration)", "why": "Your selections suggest curiosity about nature and environmental questions.",
         "skills": ["Biology or environmental science", "Data collection", "Research"],
         "project": "Track local weather or waste data and summarise the pattern."},
        {"title": "Conservation / Ecology", "why": "You may enjoy learning about ecosystems and protecting the natural world.",
         "skills": ["Observation", "Field research basics", "Scientific writing"],
         "project": "Create a small biodiversity observation log for a nearby safe area."},
        {"title": "Sustainability Analyst (exploration)", "why": "This connects environmental concerns with analysing possible improvements.",
         "skills": ["Data analysis", "Systems thinking", "Communication"],
         "project": "Compare household energy-saving ideas using a simple table."},
    ],
    "communication": [
        {"title": "Content / Science Communicator", "why": "Your choices suggest interest in explaining ideas and making information understandable.",
         "skills": ["Writing", "Fact-checking", "Presentation"],
         "project": "Turn a topic you enjoy into a one-page explainer or short presentation."},
        {"title": "Journalism / Research Writing (exploration)", "why": "You may like gathering information and communicating it clearly.",
         "skills": ["Interviewing", "Source evaluation", "Writing"],
         "project": "Write a short article using at least two reliable sources."},
        {"title": "Teaching / Training", "why": "Clear explanation and communication are central to helping others learn.",
         "skills": ["Presentation", "Lesson planning", "Listening"],
         "project": "Teach a concept in five minutes and ask the audience what was clear."},
    ],
    "organising": [
        {"title": "Project Coordinator", "why": "Your choices suggest you may enjoy planning tasks and keeping work organised.",
         "skills": ["Prioritisation", "Communication", "Task tracking"],
         "project": "Plan a small event or team assignment using a timeline and task list."},
        {"title": "Operations / Business Analyst (exploration)", "why": "This combines structured planning with finding ways to improve a process.",
         "skills": ["Spreadsheets", "Process mapping", "Analytical thinking"],
         "project": "Map a daily process and suggest one measurable improvement."},
        {"title": "Product Management (exploration)", "why": "This can involve coordinating people, understanding users, and organising product work.",
         "skills": ["Communication", "Prioritisation", "User research"],
         "project": "Write a one-page plan for improving a familiar app feature."},
    ],
}

# Scenario choices that broadly align with each personal-interest area.
# These are heuristic mappings for exploration, not validated psychometrics.
SCENARIO_ALIGNMENT = {
    "analytical": ["analytical"],
    "creative": ["creative"],
    "social": ["social", "empathetic", "collaborative"],
    "practical": ["experimental"],
    "nature": ["experimental"],
    "communication": ["communication", "collaborative", "empathetic"],
    "organising": ["organised"],
}


def build_career_recommendations(personal_scores, scenario_scores):
    """Rank career ideas using a transparent, weighted exploration heuristic.

    Personal-interest choices contribute 65% and scenario choices contribute
    35%. Scores are normalised against the strongest category in this response,
    so they are relative exploration indices, not probabilities of success.
    Logical-reasoning performance is intentionally not used to decide career fit.
    """
    categories = list(CAREER_GUIDES.keys())
    total_personal = sum(max(0, int(value or 0)) for value in personal_scores.values())
    total_scenario = sum(max(0, int(value or 0)) for value in scenario_scores.values())

    if total_personal == 0 and total_scenario == 0:
        return []

    category_data = {}
    for category in categories:
        personal_count = max(0, int(personal_scores.get(category, 0) or 0))
        aligned_types = SCENARIO_ALIGNMENT.get(category, [])
        aligned_count = sum(
            max(0, int(scenario_scores.get(scenario_type, 0) or 0))
            for scenario_type in aligned_types
        )

        personal_share = personal_count / total_personal if total_personal else 0.0
        scenario_share = aligned_count / total_scenario if total_scenario else 0.0
        raw_score = (0.65 * personal_share) + (0.35 * scenario_share)

        category_data[category] = {
            "raw_score": raw_score,
            "personal_count": personal_count,
            "personal_share": personal_share,
            "aligned_scenario_count": aligned_count,
            "scenario_share": scenario_share,
        }

    strongest_raw_score = max(
        (item["raw_score"] for item in category_data.values()),
        default=0.0,
    )
    if strongest_raw_score <= 0:
        return []

    # Rank on the combined evidence, not personal interests alone.
    ranked_categories = sorted(
        categories,
        key=lambda category: (
            -category_data[category]["raw_score"],
            -category_data[category]["personal_count"],
            -category_data[category]["aligned_scenario_count"],
            category,
        ),
    )
    ranked_categories = [
        category for category in ranked_categories
        if category_data[category]["raw_score"] > 0
    ]

    # Diversify suggestions across the strongest two areas when evidence exists.
    if len(ranked_categories) >= 2:
        category_slots = [(ranked_categories[0], 2), (ranked_categories[1], 1)]
    else:
        category_slots = [(ranked_categories[0], 3)]

    recommendations = []
    for category, slots in category_slots:
        data = category_data[category]
        relative_score = round((data["raw_score"] / strongest_raw_score) * 100)
        aligned_types = SCENARIO_ALIGNMENT.get(category, [])
        personal_pct = round(data["personal_share"] * 100)
        scenario_pct = round(data["scenario_share"] * 100)

        for career in CAREER_GUIDES.get(category, [])[:slots]:
            skills = career.get("skills", [])
            first_skill = skills[0] if skills else "the basics of this field"
            practice_skills = skills[1:3] if len(skills) > 1 else skills
            project = career.get(
                "project",
                "Create a small project that applies what you learned.",
            )

            learning_roadmap = [
                {
                    "period": "Week 1",
                    "title": "Explore the fundamentals",
                    "task": (
                        f"Start with {first_skill}. Learn the key terms and "
                        "follow one beginner tutorial or introductory lesson."
                    ),
                },
                {
                    "period": "Weeks 2–3",
                    "title": "Practise the core skills",
                    "task": (
                        "Work through small exercises and practise "
                        + ", ".join(practice_skills) + "."
                        if practice_skills
                        else "Practise with short exercises and examples."
                    ),
                },
                {
                    "period": "Week 4",
                    "title": "Build and reflect",
                    "task": (
                        project + " Write down what worked, what was difficult, "
                        "and what you want to learn next."
                    ),
                },
            ]

            personal_evidence = (
                f"{data['personal_count']} of {total_personal} personal-interest "
                f"choices ({personal_pct}%) were in this area."
                if total_personal
                else "No personal-interest choices were recorded for this response."
            )
            scenario_evidence = (
                f"{data['aligned_scenario_count']} of {total_scenario} scenario "
                f"choices ({scenario_pct}%) broadly aligned with this area."
                if total_scenario
                else "No scenario choices were recorded for this response."
            )

            recommendations.append({
                **career,
                "interest_area": category.replace("_", " ").title(),
                "match_score": relative_score,
                "match_score_type": "relative_exploration_index",
                "score_components": {
                    "personal_interest_share_percent": personal_pct,
                    "aligned_scenario_share_percent": scenario_pct,
                    "weights_percent": {
                        "personal_interests": 65,
                        "scenario_choices": 35,
                    },
                },
                "match_explanation": (
                    f"Suggested under the {category.replace('_', ' ')} interest area. "
                    f"{personal_evidence} {scenario_evidence} "
                    "The relative score compares interest patterns within this "
                    "questionnaire; it is not a probability of success or an "
                    "assessment of ability."
                ),
                "learning_roadmap": learning_roadmap,
                "roadmap_duration": "4-week starter plan",
            })

    return recommendations[:3]


@questionnaire_bp.get("/questionnaire")
def get_questionnaire():
    # Do not send correct answers or scoring keys to the frontend.
    public_questions = []

    for q in QUESTIONS:
        public_questions.append({
            "id": q["id"],
            "section": q["section"],
            "text": q["text"],
            "options": [
                {"id": key, "text": value}
                for key, value in q["options"].items()
            ]
        })

    return jsonify({
        "title": "Career Exploration Questionnaire",
        "total_questions": len(public_questions),
        "sections": [
            {"id": "personal", "title": "Personal Interests", "count": 10},
            {"id": "logical", "title": "Logical Reasoning", "count": 10},
            {"id": "scenario", "title": "Situation-Based Questions", "count": 10}
        ],
        "questions": public_questions
    })


@questionnaire_bp.post("/profile")
def calculate_profile():
    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return jsonify({"error": "Send a JSON object."}), 400

    answers = body.get("answers")

    if not isinstance(answers, dict):
        return jsonify({"error": "An 'answers' object is required."}), 400

    expected_ids = [q["id"] for q in QUESTIONS]
    missing = [qid for qid in expected_ids if qid not in answers]

    if missing:
        return jsonify({
            "error": "Some answers are missing.",
            "missing_count": len(missing),
            "missing_questions": missing
        }), 400

    invalid = [
        qid for qid in expected_ids
        if answers[qid] not in {"a", "b", "c", "d"}
    ]

    if invalid:
        return jsonify({
            "error": "Each answer must be one of a, b, c, or d.",
            "invalid_questions": invalid
        }), 400

    personal_scores = {}
    scenario_scores = {}
    correct_count = 0
    logical_count = 0

    for q in QUESTIONS:
        answer = answers[q["id"]]

        if q["section"] == "logical":
            logical_count += 1
            if answer == q["correct"]:
                correct_count += 1

        elif q["section"] == "personal":
            dimension = q["scores"][answer]
            personal_scores[dimension] = (
                personal_scores.get(dimension, 0) + 1
            )

        elif q["section"] == "scenario":
            dimension = q["scores"][answer]
            scenario_scores[dimension] = (
                scenario_scores.get(dimension, 0) + 1
            )

    career_recommendations = build_career_recommendations(
        personal_scores, scenario_scores
    )

    return jsonify({
        "status": "success",
        "profile_type": "career_exploration",
        "career_recommendations": career_recommendations,
        "logical_reasoning": {
            "correct_answers": correct_count,
            "total_questions": logical_count,
            "percentage": round(
                correct_count / logical_count * 100, 1
            )
        },
        "personal_interest_counts": personal_scores,
        "scenario_approach_counts": scenario_scores,
        "interpretation_note": (
            "This is an exploratory self-report, not a validated "
            "psychometric assessment. Logical score reflects only "
            "performance on these questions. Results do not determine "
            "intelligence, personality, or a suitable career."
        )
    }), 200
