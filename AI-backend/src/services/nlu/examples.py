"""Labelled utterances backing semantic intent matching.

This corpus replaces the old hand-tuned regex tables. It is deliberately broad
per intent — several phrasings, question forms, and statement forms — because
the matcher scores *coverage of an example* rather than the presence of a magic
keyword. Adding a new phrasing here is the intended way to teach the router,
and the same list doubles as the few-shot block for the LLM tier.
"""

from __future__ import annotations

from services.nlu.intents import StudentIntent

INTENT_EXAMPLES: dict[StudentIntent, tuple[str, ...]] = {
    StudentIntent.CLASS_LIST: (
        "what classes do you teach",
        "what classes can I sign up for",
        "what classes are available",
        "which classes do you offer",
        "can you give me a list of the classes available",
        "list the classes",
        "show me the classes you have",
        "what subjects do you teach here",
        "what courses are running now",
        "what can I join",
        "what do you offer",
        "which subjects can I study here",
        "are there any classes I can join",
        "tell me the classes you have",
        "what class options are there",
        "I want to see all your classes",
        "what other classes do you have",
        "monawada class thiyenne",
        "class mokawada thiyenne",
        "මොනවද පන්ති තියෙන්නේ",
        "පන්ති මොනවද තියෙන්නේ",
        "என்ன வகுப்புகள் இருக்கு",
    ),
    StudentIntent.CLASS_DETAIL: (
        "how much is the physics class",
        "what is the fee for A/L physics",
        "tell me about the physics class",
        "what are the details of the chemistry class",
        "how much does the class cost",
        "what is the price of the maths class",
        "class fee details",
        "give me details about A/L physics",
    ),
    StudentIntent.ENROLL: (
        "I want to join a class",
        "I want to enroll",
        "I want to sign up",
        "how do I register",
        "I would like to join the A level physics class",
        "can I register as a new student",
        "I want to join another class",
        "sign me up for chemistry",
        "I want to become a student here",
        "put me in the physics class",
        "I want to join the class",
        "class eka join karanna ona",
        "class la join panna one",
        "mata class ekata enroll wenna ona",
        "මට පන්තියට ලියාපදිංචි වෙන්න ඕන",
        "මම පන්තියට එකතු වෙන්න කැමතියි",
        "நான் வகுப்பில் சேர வேண்டும்",
    ),
    StudentIntent.MY_ENROLLMENTS: (
        "what classes have I signed up for",
        "which classes am I enrolled in",
        "can I see my class details",
        "am I enrolled",
        "what is my enrollment status",
        "which class did I register for",
        "show me my classes",
        "what classes am I in",
        "am I registered for physics",
        "do I have a class",
        "my class details",
        "what did I sign up for",
        "check my enrollment",
    ),
    StudentIntent.CANCEL_ENROLLMENT: (
        "can I cancel my enrollment at the physics class",
        "how do I cancel enrollment at the physics class",
        "what are the steps needed to cancel enrollment at the physics class",
        "I want to cancel my enrollment",
        "I want to stop coming to class",
        "how can I unenroll",
        "I would like to withdraw from the class",
        "please remove me from the physics class",
        "I want to drop this class",
        "how do I quit the class",
        "I need to discontinue my classes",
        "cancel my registration",
    ),
    StudentIntent.TUTOR_INFO: (
        "who is the tutor",
        "can I get some information on the tutor",
        "who are the team at this academy",
        "tell me about the teacher",
        "what are the tutor qualifications",
        "who teaches the physics class",
        "who runs this centre",
        "information about the teaching staff",
        "who will be my teacher",
        "tell me about the tutors here",
        "what is the background of the tutor",
        "who are the staff members",
        "details of the teaching team",
        "ගුරුවරයා කවුද",
        "sir kawuda",
        "ஆசிரியர் யார்",
    ),
    StudentIntent.CENTRE_INFO: (
        "tell me about the academy",
        "where are you located",
        "what is your contact number",
        "tell me about this institute",
        "what is this tuition centre",
        "how can I contact the office",
        "what is your address",
    ),
    StudentIntent.SCHEDULE: (
        "what is the schedule for my physics class",
        "when is my next class",
        "what time is the class today",
        "do I have class tomorrow",
        "show me my timetable",
        "what days are the classes",
        "when does the physics class start",
        "my weekly schedule",
        "what time does class begin",
        "is there class today",
        "class times please",
        "මගේ පන්තියේ වේලාව මොකක්ද",
        "ada class ekak thiyenawada",
        "என் வகுப்பு நேரம் என்ன",
    ),
    StudentIntent.RESOURCE_FILES: (
        "do you have past papers",
        "send me the tutes",
        "can I get the model papers",
        "I need the syllabus pdf",
        "what textbooks do you have",
        "send me the notes",
        "download the physics papers",
        "any tutes for chemistry",
        "share the past paper for 2023",
        "what papers are available",
        "what tutes are available",
        "can I have tutes",
        "any tutes",
        "paper eka ewanna",
        "notes anuppunga",
        "පේපර්ස් තියෙනවද",
        "නෝට්ස් එවන්න",
        "பேப்பர் இருக்கா",
    ),
    StudentIntent.LESSON_HELP: (
        "explain velocity to me",
        "what is terminal velocity",
        "I don't understand momentum",
        "help me with this lesson",
        "can you explain the mole concept",
        "what did the tutor teach about friction",
        "explain this topic from the notes",
        "explain this from the uploaded notes",
        "explain this lesson from the notes",
        "මේ පාඩම් notes ටික explain කරන්න",
        "what is acceleration",
        "teach me about newtons laws",
        "I need help understanding the chapter",
        "meka kiyala denna",
        "මට මේක පැහැදිලි කරලා දෙන්න",
    ),
    StudentIntent.PAYMENT_SUBMIT: (
        "I sent my bank slip",
        "here is my payment receipt",
        "I paid the fee",
        "I have made the payment",
        "sending the payment slip now",
        "I transferred the money",
        "attached is my bank slip",
        "can I pay via paypal",
        "how do I pay the fee",
        "what payment methods do you accept",
        "I paid the fee and I am sending the slip",
        "I paid the fee and I am sending the receipt",
        "mama gaasthuwa gewuwa",
        "fee eka geewuwa slip eka yawanawa",
        "මම ගාස්තුව ගෙවුවා",
        "ගාස්තු ගෙවුවා රිසිට් එක යවනවා",
        "රිසිට් එක එවනවා",
        "கட்டணம் கட்டிட்டேன் ரசீது அனுப்புறேன்",
    ),
    StudentIntent.PAYMENT_STATUS: (
        "did you receive my payment",
        "has my payment been confirmed",
        "is my fee paid",
        "check my payment status",
        "was my bank slip approved",
        "did my payment go through",
    ),
    StudentIntent.ESCALATION: (
        "I need to speak with the tutor urgently",
        "can I talk to a human",
        "I want to talk to the tutor",
        "I want to speak to the teacher",
        "please connect me to the teacher",
        "I have a complaint",
        "I need to inform the tutor I will be absent",
        "I want to ask the tutor to reschedule",
        "can someone from the staff call me",
        "I need urgent help from a person",
        "let me speak to sir",
        "sir ekata katha karanna ona",
        "ගුරුවරයාට කතා කරන්න ඕනේ",
        "ஆசிரியரிடம் பேசணும்",
    ),
    StudentIntent.PROFILE_LOOKUP: (
        "who am I",
        "what is my name",
        "what details do you have about me",
        "what is my phone number on file",
    ),
    StudentIntent.GREETING: (
        "hi",
        "hello",
        "hey there",
        "good morning",
        "thanks",
        "thank you so much",
        "ok",
        "bye",
        "see you",
    ),
}

#: Compact few-shot block handed to the LLM tier. Kept short on purpose — the
#: full corpus above is for lexical matching, the LLM only needs the taxonomy
#: plus one disambiguating example per tricky pair.
LLM_FEW_SHOT = """\
"What classes do you teach?" -> class_list
"Can you give me a list of the classes available" -> class_list
"What classes have I signed up for?" -> my_enrollments
"Can I see my class details?" -> my_enrollments
"I want to join another class" -> enroll
"How do I cancel enrollment at the Physics class?" -> cancel_enrollment
"Can I cancel my enrollment at the physics class?" -> cancel_enrollment
"Can I get some information on the tutor" -> tutor_info
"Who are the team at Demo Physics Academy?" -> tutor_info
"What is the schedule for my physics clss" -> schedule
"Do you have 2023 past papers?" -> resource_files
"What is terminal velocity" -> lesson_help
"I sent my bank slip" -> payment_submit
"Did you receive my payment?" -> payment_status
"I need to speak with the tutor urgently" -> escalation
"Man you suck f%$ you" -> off_topic
"Why do you suck so bad" -> off_topic
"What is the weather today?" -> off_topic
"hi" -> greeting
"""
