"""Canned WhatsApp strings for en / si / ta. LLM-generated replies use mirroring instead."""

from __future__ import annotations

from services.language.detect import canned_language_parent, normalize_canned_language

STRINGS: dict[str, dict[str, str]] = {
    "out_of_scope": {
        "en": (
            "I'm here to help with tuition-related things — joining classes, past papers, "
            "lesson topics, fees, and speaking to your tutor.\n\n"
            "That question is a bit outside what I can help with here. "
            "Feel free to ask me about your class or enrollment!"
        ),
        "si": (
            "මම උදව් කරන්නේ ඉගෙනුම් පන්තිවලට එකතු වීම, පේපර්, පාඩම්, ගාස්තු "
            "සහ ගුරුවරයා සමඟ කතා කිරීම වගේ දේවල්වලටයි.\n\n"
            "ඒ ප්‍රශ්නය මගේ පරාසයෙන් මඳක් එහායි. පන්තිය හෝ ලියාපදිංචිය ගැන අහන්න!"
        ),
        "ta": (
            "நான் வகுப்பில் சேர, பாடத் தாள்கள், பாடங்கள், கட்டணம், "
            "ஆசிரியரிடம் பேசுவது போன்ற கல்வி விஷயங்களுக்கு உதவுவேன்.\n\n"
            "அந்தக் கேள்வி என் வரம்பிற்கு சற்று வெளியே. வகுப்பு அல்லது சேர்க்கை பற்றி கேளுங்கள்!"
        ),
    },
    "voice_fail": {
        "en": "Sorry, I couldn't understand that voice message. Could you please try again?",
        "si": "සමාවන්න, ඒ හඬ පණිවිඩය තේරුම් ගන්න බැරි වුණා. ආයෙත් උත්සාහ කරන්න පුළුවන්ද?",
        "ta": "மன்னிக்கவும், அந்த குரல் செய்தியை புரிந்துகொள்ள முடியவில்லை. மீண்டும் முயல்கிறீர்களா?",
    },
    "unsupported_audio": {
        "en": "Sorry, I can only process voice notes (not audio files). Please record a voice message instead.",
        "si": "සමාවන්න, මට පුළුවන් voice notes විතරයි. Audio file එකක් නෙවෙයි — හඬ පණිවිඩයක් record කරන්න.",
        "ta": "மன்னிக்கவும், குரல் குறிப்புகளை மட்டுமே செயலாக்க முடியும் (ஒலிக் கோப்புகள் அல்ல). குரல் செய்தி பதிவு செய்யுங்கள்.",
    },
    "technical_issue": {
        "en": (
            "Thanks for messaging {tenant_name}! We're having a brief technical issue. "
            "Please try again in a moment."
        ),
        "si": "ස්තූතියි {tenant_name} වෙත message කළාට! ටිකක් technical issue එකක් තියෙනවා. මොහොතකින් ආයෙත් උත්සාහ කරන්න.",
        "ta": "{tenant_name}க்கு செய்தி அனுப்பியதற்கு நன்றி! சிறிய தொழில்நுட்ப சிக்கல். சற்று நேரம் கழித்து மீண்டும் முயலுங்கள்.",
    },
    "escalation_confirm": {
        "en": "Would you like me to send this question to your tutor?",
        "si": "මේ ප්‍රශ්නය ගුරුවරයාට යවන්නද?",
        "ta": "இந்தக் கேள்வியை உங்கள் ஆசிரியருக்கு அனுப்பட்டுமா?",
    },
    "escalation_declined": {
        "en": "No problem — I won't send it to the tutor. You can ask me something else anytime.",
        "si": "කමක් නෑ — ගුරුවරයාට යවන්නේ නෑ. වෙන දෙයක් අහන්න පුළුවන්.",
        "ta": "பரவாயில்லை — ஆசிரியருக்கு அனுப்ப மாட்டேன். வேறு எதையும் கேட்கலாம்.",
    },
    "onboarding_ask_name": {
        "en": "Hi! Welcome to {tenant_name} — I'll help you get enrolled. What's your full name?",
        "si": "ආයුබෝවන්! {tenant_name} වෙත සාදරයෙන් පිළිගනිමු — ලියාපදිංචි වෙන්න උදව් කරනවා. ඔබේ සම්පූර්ණ නම කුමක්ද?",
        "ta": "வணக்கம்! {tenant_name}க்கு வரவேற்கிறோம் — சேர்க்கைக்கு உதவுவேன். உங்கள் முழுப் பெயர் என்ன?",
    },
    "onboarding_restart": {
        "en": "No problem — let's start over. What's your full name?",
        "si": "කමක් නෑ — ආයෙත් පටන් ගමු. ඔබේ සම්පූර්ණ නම කුමක්ද?",
        "ta": "பரவாயில்லை — மீண்டும் தொடங்குவோம். உங்கள் முழுப் பெயர் என்ன?",
    },
    "onboarding_ask_school": {
        "en": "Nice to meet you{name_suffix}! Which school do you go to?",
        "si": "හමුවීම සතුටක්{name_suffix}! ඔබ යන පාසල කුමක්ද?",
        "ta": "சந்தித்ததில் மகிழ்ச்சி{name_suffix}! நீங்கள் எந்தப் பாடசாலைக்குச் செல்கிறீர்கள்?",
    },
    "onboarding_ask_district": {
        "en": "Got it. Which district are you in?",
        "si": "හරි. ඔබේ දිස්ත්‍රික්කය කුමක්ද?",
        "ta": "சரி. நீங்கள் எந்த மாவட்டத்தைச் சேர்ந்தவர்?",
    },
    "class_catalog_header_named": {
        "en": "Thanks, {first}! At {tenant_name} we currently offer these classes:",
        "si": "ස්තූතියි, {first}! {tenant_name} හි දැන් තියෙන පන්ති:",
        "ta": "நன்றி, {first}! {tenant_name} தற்போது வழங்கும் வகுப்புகள்:",
    },
    "class_catalog_header": {
        "en": "Here are the classes available at {tenant_name}:",
        "si": "{tenant_name} හි තියෙන පන්ති මෙන්න:",
        "ta": "{tenant_name} இல் உள்ள வகுப்புகள்:",
    },
    "class_catalog_pick": {
        "en": "Reply with the class name or number when you're ready to pick one.",
        "si": "පන්තිය තෝරන්න නම හෝ අංකයෙන් reply කරන්න.",
        "ta": "வகுப்பைத் தேர்ந்தெடுக்க பெயர் அல்லது எண்ணை அனுப்புங்கள்.",
    },
    "class_catalog_empty": {
        "en": "We don't have any open classes listed right now — please contact the office.",
        "si": "දැන් open පන්ති ලැයිස්තුවේ නෑ — කාර්යාලයට කතා කරන්න.",
        "ta": "இப்போது திறந்த வகுப்புகள் இல்லை — அலுவலகத்தைத் தொடர்பு கொள்ளுங்கள்.",
    },
    "review_confirmation": {
        "en": (
            "Please review your enrollment details for {tenant_name}:\n\n"
            "• **Full name:** {name}\n"
            "• **Contact number:** {contact}\n"
            "• **School:** {school}\n"
            "• **District:** {district}\n"
            "• **Course:** {class_label}{fee_line}\n\n"
            "By confirming, you agree to our data policy.\n"
            "Shall I confirm your enrollment? Reply **YES** to proceed."
        ),
        "si": (
            "{tenant_name} සඳහා ඔබේ ලියාපදිංචි විස්තර බලන්න:\n\n"
            "• **සම්පූර්ණ නම:** {name}\n"
            "• **දුරකථනය:** {contact}\n"
            "• **පාසල:** {school}\n"
            "• **දිස්ත්‍රික්කය:** {district}\n"
            "• **පාඨමාලාව:** {class_label}{fee_line}\n\n"
            "Confirm කරනකොට අපේ data policy එකට එකඟ වෙනවා.\n"
            "ලියාපදිංචිය confirm කරන්නද? **YES** / **ඔව්** කියලා reply කරන්න."
        ),
        "ta": (
            "{tenant_name} சேர்க்கை விவரங்களைப் பாருங்கள்:\n\n"
            "• **முழுப் பெயர்:** {name}\n"
            "• **தொலைபேசி:** {contact}\n"
            "• **பாடசாலை:** {school}\n"
            "• **மாவட்டம்:** {district}\n"
            "• **பாடநெறி:** {class_label}{fee_line}\n\n"
            "உறுதிப்படுத்துவதன் மூலம் தரவுக் கொள்கையை ஏற்கிறீர்கள்.\n"
            "சேர்க்கையை உறுதிப்படுத்தவா? **YES** / **ஆம்** என பதிலளிக்கவும்."
        ),
    },
    "fee_line": {
        "en": "\nClass fee: LKR {fee}/month.",
        "si": "\nපන්ති ගාස්තුව: LKR {fee}/මාසය.",
        "ta": "\nவகுப்புக் கட்டணம்: LKR {fee}/மாதம்.",
    },
    "disambiguation_header": {
        "en": "A few classes match what you said — which one would you like?",
        "si": "කිහිපයක් match වෙනවා — කුමන පන්තියද?",
        "ta": "சில வகுப்புகள் பொருந்துகின்றன — எதைத் தேர்ந்தெடுக்கிறீர்கள்?",
    },
    "disambiguation_pick": {
        "en": "Reply with the number or full class name.",
        "si": "අංකයෙන් හෝ පන්ති නමින් reply කරන්න.",
        "ta": "எண் அல்லது முழு வகுப்புப் பெயரை அனுப்புங்கள்.",
    },
    "enrollment_welcome": {
        "en": (
            "Welcome to {tenant_name}! Thank you for your enrollment in **{class_label}**.\n\n"
            "Our staff will review your request and get back to you soon. "
            "Please proceed with the payment to continue your enrollment — "
            "send a photo of your **payment receipt / bank slip** on WhatsApp.\n\n"
            "We also have **tutes** and **past papers** for your class. "
            "If you'd like them now, just ask me (e.g. “send me a past paper”) — "
            "or you can collect them physically from the class."
        ),
        "si": (
            "{tenant_name} වෙත සාදරයෙන් පිළිගනිමු! **{class_label}** සඳහා ලියාපදිංචි වූවාට ස්තූතියි.\n\n"
            "කාර්ය මණ්ඩලය ඉල්ලීම බලලා ඉක්මනින් ආපසු කියනවා. ලියාපදිංචිය ඉදිරියට ගෙන යන්න "
            "**ගෙවීම් රිසිට්පත / bank slip** එකේ ඡායාරූපයක් WhatsApp එකෙන් යවන්න.\n\n"
            "ඔබේ පන්තියට **tutes** සහ **past papers** තියෙනවා. ඕනෑ නම් දැන් අහන්න "
            "(උදා: “past paper එකක් එවන්න”) — නැත්නම් පන්තියෙන් physical ගන්න පුළුවන්."
        ),
        "ta": (
            "{tenant_name}க்கு வரவேற்கிறோம்! **{class_label}** சேர்க்கைக்கு நன்றி.\n\n"
            "பணியாளர்கள் கோரிக்கையைப் பார்த்து விரைவில் பதிலளிப்பார்கள். சேர்க்கையைத் தொடர "
            "**கட்டண ரசீது / வங்கிச் சிலிப்** புகைப்படத்தை WhatsApp இல் அனுப்புங்கள்.\n\n"
            "உங்கள் வகுப்புக்கு **tutes** மற்றும் **past papers** உண்டு. வேண்டுமானால் இப்போது கேளுங்கள் "
            "(எ.கா. “past paper அனுப்பு”) — அல்லது வகுப்பில் நேரில் பெற்றுக்கொள்ளலாம்."
        ),
    },
    "payment_pending": {
        "en": (
            "Thanks, {name}! Your application for **{class_label}** at {tenant_name} "
            "is almost complete.{fee_line}\n\n"
            "Please send a photo of your **payment receipt / bank slip** on WhatsApp "
            "to confirm your enrollment."
        ),
        "si": (
            "ස්තූතියි, {name}! {tenant_name} හි **{class_label}** සඳහා ඔබේ අයදුම්පත "
            "අවසන් වෙන්න ළඟයි.{fee_line}\n\n"
            "ලියාපදිංචිය confirm කරන්න **ගෙවීම් රිසිට්පත / bank slip** ඡායාරූපයක් WhatsApp එකෙන් යවන්න."
        ),
        "ta": (
            "நன்றி, {name}! {tenant_name} இல் **{class_label}** விண்ணப்பம் "
            "முடியும் தருவாயில் உள்ளது.{fee_line}\n\n"
            "சேர்க்கையை உறுதிப்படுத்த **கட்டண ரசீது / வங்கிச் சிலிப்** புகைப்படத்தை WhatsApp இல் அனுப்புங்கள்."
        ),
    },
    "receipt_received": {
        "en": (
            "Thanks! We received your payment receipt for {tenant_name}. "
            "Our team is reviewing it now — you'll get a confirmation message once "
            "your enrollment is approved."
        ),
        "si": (
            "ස්තූතියි! {tenant_name} සඳහා ගෙවීම් රිසිට්පත ලැබුණා. "
            "කණ්ඩායම දැන් බලනවා — ලියාපදිංචිය අනුමත වුණාම confirmation එකක් එනවා."
        ),
        "ta": (
            "நன்றி! {tenant_name} கட்டண ரசீது கிடைத்தது. "
            "குழு இப்போது பார்க்கிறது — சேர்க்கை அங்கீகரிக்கப்பட்டதும் உறுதிப்படுத்தல் வரும்."
        ),
    },
    "awaiting_review": {
        "en": (
            "Your payment receipt is already with our team at {tenant_name}. "
            "We'll message you as soon as your enrollment is confirmed."
        ),
        "si": "{tenant_name} කණ්ඩායමට ඔබේ රිසිට්පත දැනටමත් තියෙනවා. ලියාපදිංචිය confirm වුණාම message කරනවා.",
        "ta": "{tenant_name} குழுவிடம் உங்கள் ரசீது ஏற்கனவே உள்ளது. சேர்க்கை உறுதிப்பட்டதும் செய்தி அனுப்புவோம்.",
    },
    "enrollment_success": {
        "en": (
            "Great news, {name}!\n"
            "You are **successfully enrolled** in {class_label} at {tenant_name}.\n"
            "Welcome — class details and fee info will follow shortly."
        ),
        "si": (
            "සුබ පුවතක්, {name}!\n"
            "ඔබ {tenant_name} හි {class_label} වෙත **සාර්ථකව ලියාපදිංචි** වෙලා.\n"
            "සාදරයෙන් පිළිගනිමු — පන්ති විස්තර සහ ගාස්තු ඉක්මනින් එනවා."
        ),
        "ta": (
            "நற்செய்தி, {name}!\n"
            "நீங்கள் {tenant_name} இல் {class_label} இல் **வெற்றிகரமாக சேர்க்கப்பட்டுள்ளீர்கள்**.\n"
            "வரவேற்கிறோம் — வகுப்பு விவரங்களும் கட்டணமும் விரைவில் வரும்."
        ),
    },
    "payment_rejected": {
        "en": (
            "Hi {name}, we couldn't verify your payment receipt at {tenant_name}. "
            "Please send a clear photo of your bank slip again, or contact the office for help."
        ),
        "si": (
            "හායි {name}, {tenant_name} හි ගෙවීම් රිසිට්පත verify කරන්න බැරි වුණා. "
            "පැහැදිලි bank slip ඡායාරූපයක් ආයෙත් යවන්න, නැත්නම් කාර්යාලයට කතා කරන්න."
        ),
        "ta": (
            "ஹாய் {name}, {tenant_name} இல் கட்டண ரசீதை உறுதிப்படுத்த முடியவில்லை. "
            "தெளிவான வங்கிச் சிலிப் புகைப்படத்தை மீண்டும் அனுப்புங்கள், அல்லது அலுவலகத்தைத் தொடர்பு கொள்ளுங்கள்."
        ),
    },
    "already_registered": {
        "en": "Hi {name}! You're already registered at {tenant_name} for {class_label}. How can I help you today?",
        "si": "හායි {name}! ඔබ දැනටමත් {tenant_name} හි {class_label} සඳහා ලියාපදිංචියි. අද මොනවද උදව් කරන්නද?",
        "ta": "ஹாய் {name}! நீங்கள் ஏற்கனவே {tenant_name} இல் {class_label}க்கு பதிவு செய்துள்ளீர்கள். இன்று எப்படி உதவலாம்?",
    },
    "not_registered": {
        "en": (
            "I don't have you registered at **{tenant_name}** yet, "
            "so you're not enrolled in a class.\n\n"
            "If you'd like to join, just say **I'd like to enroll** and I'll help you get started."
        ),
        "si": (
            "ඔබ තාම **{tenant_name}** හි ලියාපදිංචි වෙලා නෑ, ඒ නිසා පන්තියකටත් එකතු වෙලා නෑ.\n\n"
            "එකතු වෙන්න ඕන නම් **මට enroll වෙන්න ඕන** කියලා කියන්න — මම උදව් කරනවා."
        ),
        "ta": (
            "நீங்கள் இன்னும் **{tenant_name}** இல் பதிவு செய்யவில்லை, எனவே வகுப்பில் சேரவில்லை.\n\n"
            "சேர விரும்பினால் **நான் சேர விரும்புகிறேன்** என்று சொல்லுங்கள் — நான் உதவுவேன்."
        ),
    },
    "onboarding_interest": {
        "en": (
            "Thanks for your interest in {tenant_name}! "
            "When you're ready to enroll, just say you'd like to join a class."
        ),
        "si": "{tenant_name} ගැන උනන්දුවට ස්තූතියි! ලියාපදිංචි වෙන්න ready නම්, පන්තියකට join වෙන්න කියලා කියන්න.",
        "ta": "{tenant_name} ஆர்வத்திற்கு நன்றி! சேர தயாரானால், ஒரு வகுப்பில் சேர விரும்புகிறேன் என்று சொல்லுங்கள்.",
    },
    "missing_enrollment_details": {
        "en": "Some enrollment details are missing. Let's start again — what is your full name?",
        "si": "ලියාපදිංචි විස්තර කිහිපයක් අඩුයි. ආයෙත් පටන් ගමු — ඔබේ සම්පූර්ණ නම කුමක්ද?",
        "ta": "சில சேர்க்கை விவரங்கள் இல்லை. மீண்டும் தொடங்குவோம் — உங்கள் முழுப் பெயர் என்ன?",
    },
    "need_contact_details": {
        "en": "I need your contact details to complete registration. Please try again.",
        "si": "ලියාපදිංචිය අවසන් කරන්න ඔබේ සම්බන්ධතා විස්තර ඕනේ. ආයෙත් උත්සාහ කරන්න.",
        "ta": "பதிவை முடிக்க உங்கள் தொடர்பு விவரம் தேவை. மீண்டும் முயலுங்கள்.",
    },
    "payment_ack": {
        "en": (
            "Thanks! We received your payment receipt for {tenant_name}.\n\n"
            "Our team will verify it shortly and confirm your enrollment. "
            "You'll hear back here on WhatsApp once it's approved."
        ),
        "si": (
            "ස්තූතියි! {tenant_name} සඳහා ගෙවීම් රිසිට්පත ලැබුණා.\n\n"
            "කණ්ඩායම ඉක්මනින් verify කරලා ලියාපදිංචිය confirm කරනවා. අනුමත වුණාම WhatsApp එකෙන් කියනවා."
        ),
        "ta": (
            "நன்றி! {tenant_name} கட்டண ரசீது கிடைத்தது.\n\n"
            "குழு விரைவில் சரிபார்த்து சேர்க்கையை உறுதிப்படுத்தும். அங்கீகரிக்கப்பட்டதும் WhatsApp இல் தெரிவிப்போம்."
        ),
    },
    "payment_missing_media": {
        "en": (
            "To verify your payment at {tenant_name}, please send a clear photo "
            "of your bank slip or payment receipt.\n\n"
            "Once we have the image, our team can review and confirm your enrollment."
        ),
        "si": (
            "{tenant_name} හි ගෙවීම verify කරන්න bank slip හෝ රිසිට්පතේ පැහැදිලි ඡායාරූපයක් යවන්න.\n\n"
            "පින්තූරය ආවාම කණ්ඩායම බලලා ලියාපදිංචිය confirm කරනවා."
        ),
        "ta": (
            "{tenant_name} கட்டணத்தை உறுதிப்படுத்த வங்கிச் சிலிப் அல்லது ரசீதின் தெளிவான புகைப்படத்தை அனுப்புங்கள்.\n\n"
            "படம் கிடைத்ததும் குழு பார்த்து சேர்க்கையை உறுதிப்படுத்தும்."
        ),
    },
    "payment_need_profile": {
        "en": "I need your profile to process a payment receipt. Please try again.",
        "si": "ගෙවීම් රිසිට්පත process කරන්න ඔබේ profile එක ඕනේ. ආයෙත් උත්සාහ කරන්න.",
        "ta": "கட்டண ரசீதை செயலாக்க உங்கள் சுயவிவரம் தேவை. மீண்டும் முயலுங்கள்.",
    },
    "escalation_ack": {
        "en": (
            "We've notified your tutor at {tenant_name}. They'll get back to you soon.\n\n"
            "You can keep chatting here in the meantime — I'm still happy to help with class questions or resources."
        ),
        "si": (
            "{tenant_name} හි ගුරුවරයාට දැනුම් දුන්නා. ඉක්මනින් ආපසු කතා කරයි.\n\n"
            "එතෙක් මෙහි කතා කරන්න පුළුවන් — පන්ති ප්‍රශ්න හෝ resources වලට තවම උදව් කරනවා."
        ),
        "ta": (
            "{tenant_name} ஆசிரியருக்கு தெரிவித்துவிட்டோம். விரைவில் பதிலளிப்பார்கள்.\n\n"
            "இதற்கிடையில் இங்கே பேசலாம் — வகுப்புக் கேள்விகள் அல்லது வளங்களுக்கு இன்னும் உதவுவேன்."
        ),
    },
    "escalation_low_confidence": {
        "en": "Done — I've sent your question to {tenant_name} for review. A tutor can follow up with you.",
        "si": "හරි — ඔබේ ප්‍රශ්නය {tenant_name} වෙත review එකට යැව්වා. ගුරුවරයෙක් follow up කරයි.",
        "ta": "முடிந்தது — உங்கள் கேள்வியை {tenant_name} பார்வைக்கு அனுப்பினேன். ஆசிரியர் தொடர்ந்து பேசுவார்.",
    },
    "escalation_need_id": {
        "en": "I'll connect you with a tutor shortly. Please try again if this persists.",
        "si": "ගුරුවරයෙක් සමඟ ඉක්මනින් සම්බන්ධ කරනවා. ආයෙත් වුණොත් නැවත උත්සාහ කරන්න.",
        "ta": "ஆசிரியருடன் விரைவில் இணைப்பேன். தொடர்ந்தால் மீண்டும் முயலுங்கள்.",
    },
    "rag_empty_enrolled": {
        "en": (
            "I couldn't find tutor notes for your enrolled class(es) on that topic. "
            "Try rephrasing or ask your tutor in class."
        ),
        "si": "ඒ මාතෘකාවට ඔබේ පන්තියේ tutor notes හම්බුණේ නෑ. වෙන විදිහකින් අහන්න, නැත්නම් පන්තියේදී ගුරුවරයාගෙන් අහන්න.",
        "ta": (
            "அந்தத் தலைப்பில் உங்கள் வகுப்பின் ஆசிரியர் குறிப்புகள் கிடைக்கவில்லை. "
            "வேறுவிதமாகக் கேளுங்கள் அல்லது வகுப்பில் ஆசிரியரிடம் கேளுங்கள்."
        ),
    },
    "rag_empty": {
        "en": "I couldn't find relevant tutor notes for that question. Try rephrasing or ask your tutor in class.",
        "si": "ඒ ප්‍රශ්නයට ගැලපෙන tutor notes හම්බුණේ නෑ. වෙන විදිහකින් අහන්න, නැත්නම් පන්තියේදී ගුරුවරයාගෙන් අහන්න.",
        "ta": "அந்தக் கேள்விக்கு பொருத்தமான ஆசிரியர் குறிப்புகள் இல்லை. வேறுவிதமாகக் கேளுங்கள் அல்லது வகுப்பில் ஆசிரியரிடம் கேளுங்கள்.",
    },
    "rag_not_indexed": {
        "en": "I don't have tutor notes indexed for your class yet. Please ask your tutor directly or try again later.",
        "si": "ඔබේ පන්තියට තාම tutor notes index වෙලා නෑ. ගුරුවරයාගෙන් කෙලින්ම අහන්න, නැත්නම් පසුව උත්සාහ කරන්න.",
        "ta": "உங்கள் வகுப்புக்கு ஆசிரியர் குறிப்புகள் இன்னும் அட்டவணையில் இல்லை. நேரடியாக ஆசிரியரிடம் கேளுங்கள் அல்லது பின்னர் முயலுங்கள்.",
    },
    "rag_low_confidence_escalated": {
        "en": (
            "I couldn't find enough reliable information in your tutor's notes "
            "to answer that confidently. I've sent this to your tutor for review."
        ),
        "si": "විශ්වාසයෙන් උත්තර දෙන්න තරම් tutor notes එකේ තොරතුරු නෑ. මේක ගුරුවරයාට review එකට යැව්වා.",
        "si_latn": (
            "Wishwasayen uttara denna tharam tutor notes eke thiyenne na. "
            "Meeka guruthumyata review ekata yewwa."
        ),
        "ta": "நம்பிக்கையுடன் பதில் சொல்ல போதிய குறிப்புகள் இல்லை. இதை ஆசிரியர் பார்வைக்கு அனுப்பினேன்.",
        "ta_latn": "Nambikaiya pathil solla notes podhum illa. Ithai teacher kitta anuppitten.",
    },
    "drive_folder_papers": {
        "en": "papers and tutes",
        "si": "පේපර් සහ tutes",
        "si_latn": "papers saha tutes",
        "ta": "பாடத் தாள்களும் tutes-உம்",
        "ta_latn": "papers and tutes",
    },
    "drive_folder_textbooks": {
        "en": "textbooks",
        "si": "පෙළපොත්",
        "si_latn": "textbooks",
        "ta": "பாடப்புத்தகங்கள்",
        "ta_latn": "textbooks",
    },
    "drive_folder_syllabus": {
        "en": "syllabus files",
        "si": "විෂය නිර්දේශ ගොනු",
        "si_latn": "syllabus files",
        "ta": "பாடத்திட்டக் கோப்புகள்",
        "ta_latn": "syllabus files",
    },
    "drive_folder_files": {
        "en": "files",
        "si": "ගොනු",
        "si_latn": "files",
        "ta": "கோப்புகள்",
        "ta_latn": "files",
    },
    "drive_list": {
        "en": (
            "Here are the available {folder_label}:\n\n"
            "{file_list}\n\n"
            "Reply with the number of the file you want."
        ),
        "si": (
            "තියෙන {folder_label} මෙන්න:\n\n"
            "{file_list}\n\n"
            "ඕනේ file එකේ අංකයෙන් reply කරන්න."
        ),
        "si_latn": (
            "Thiyena {folder_label} me wage:\n\n"
            "{file_list}\n\n"
            "Ona file eke number eken reply karanna."
        ),
        "ta": (
            "கிடைக்கும் {folder_label}:\n\n"
            "{file_list}\n\n"
            "வேண்டிய கோப்பின் எண்ணை அனுப்புங்கள்."
        ),
        "ta_latn": (
            "Available {folder_label}:\n\n"
            "{file_list}\n\n"
            "Ona file number ah anuppu."
        ),
    },
    "drive_list_range": {
        "en": (
            "That number is not on the list. Reply with a number from 1 to {count}:\n\n"
            "{file_list}"
        ),
        "si": "ඒ අංකය ලැයිස්තුවේ නෑ. 1 සිට {count} දක්වා අංකයකින් reply කරන්න:\n\n{file_list}",
        "si_latn": (
            "Eka number eka list eke na. 1 idan {count} wenakam number eken reply karanna:\n\n"
            "{file_list}"
        ),
        "ta": "அந்த எண் பட்டியலில் இல்லை. 1 முதல் {count} வரை அனுப்புங்கள்:\n\n{file_list}",
        "ta_latn": "Andha number list la illa. 1 to {count} kuulla anuppu:\n\n{file_list}",
    },
    "drive_pick": {
        "en": "Here's the file you picked:\n\n{filename}\n{link}",
        "si": "ඔබ තෝරපු file එක:\n\n{filename}\n{link}",
        "si_latn": "Oya select kare file eka:\n\n{filename}\n{link}",
        "ta": "நீங்கள் தேர்ந்தெடுத்த கோப்பு:\n\n{filename}\n{link}",
        "ta_latn": "Neenga pick panna file:\n\n{filename}\n{link}",
    },
    "drive_empty": {
        "en": (
            "I couldn't find any {folder_label} in Drive right now. "
            "Please check with {tenant_name}."
        ),
        "si": "දැන් Drive එකේ {folder_label} හම්බුණේ නෑ. {tenant_name} එක්ක බලන්න.",
        "si_latn": "Dhan Drive eke {folder_label} hambune na. {tenant_name} ekka check karanna.",
        "ta": "இப்போது Drive-இல் {folder_label} இல்லை. {tenant_name}ஐப் பாருங்கள்.",
        "ta_latn": "Ippo Drive la {folder_label} illa. {tenant_name} kitta check pannunga.",
    },
    "drive_error": {
        "en": (
            "Sorry — I couldn't search for files right now. "
            "Please try again in a moment or contact your tuition centre."
        ),
        "si": "සමාවන්න — දැන් files search කරන්න බැරි වුණා. මොහොතකින් ආයෙත් උත්සාහ කරන්න, නැත්නම් පන්තියට කතා කරන්න.",
        "si_latn": (
            "Sorry — dhan files search karanna bari una. "
            "Mohothakin ayeth try karanna, nathnam class ekata katha karanna."
        ),
        "ta": "மன்னிக்கவும் — இப்போது கோப்புகளைத் தேட முடியவில்லை. சற்று நேரம் கழித்து முயலுங்கள் அல்லது நிலையத்தைத் தொடர்பு கொள்ளுங்கள்.",
        "ta_latn": "Sorry — ippo files search panna mudiyala. Konjam neram kalichu try pannunga.",
    },
    "resource_not_enrolled": {
        "en": (
            "Past papers and tutor notes are available to enrolled students only.\n\n"
            "Reply \"join class\" or complete your enrollment at {tenant_name} to get access!"
        ),
        "si": (
            "පේපර් සහ tutor notes තියෙන්නේ ලියාපදිංචි සිසුන්ට විතරයි.\n\n"
            "\"join class\" කියලා කියන්න, නැත්නම් {tenant_name} හි ලියාපදිංචිය අවසන් කරන්න."
        ),
        "si_latn": (
            "Papers saha tutor notes thiyenne enroll una studentlata witharayi.\n\n"
            "\"join class\" kiyala kiyanna, nathnam {tenant_name} eke enrollment eka iwara karanna."
        ),
        "ta": (
            "பாடத் தாள்களும் குறிப்புகளும் சேர்ந்த மாணவர்களுக்கு மட்டுமே.\n\n"
            "\"join class\" என்று சொல்லுங்கள் அல்லது {tenant_name} சேர்க்கையை முடியுங்கள்."
        ),
        "ta_latn": (
            "Papers and notes enrolled students kitta dhaan irukku.\n\n"
            "\"join class\" nu sollunga, illati {tenant_name} enrollment finish pannunga."
        ),
    },
    "resource_no_enrollment": {
        "en": (
            "I couldn't find an active class enrollment for your account. "
            "Please contact {tenant_name} to confirm your enrollment."
        ),
        "si": "ඔබේ account එකට active පන්ති ලියාපදිංචියක් හම්බුණේ නෑ. {tenant_name} එක්ක බලන්න.",
        "si_latn": (
            "Oya account ekata active class enrollment ekak hambune na. "
            "{tenant_name} ekka check karanna."
        ),
        "ta": "உங்கள் கணக்கில் செயலில் உள்ள வகுப்புச் சேர்க்கை இல்லை. {tenant_name}ஐத் தொடர்பு கொள்ளுங்கள்.",
        "ta_latn": "Ungal account la active class enrollment illa. {tenant_name} kitta check pannunga.",
    },
    "resource_rag_header": {
        "en": "Based on your tutor's notes:\n\n{answer}\n\nSources: {citations}",
        "si": "ගුරුවරයාගේ notes අනුව:\n\n{answer}\n\nමූලාශ්‍ර: {citations}",
        "si_latn": "Guru notes walata anuwa:\n\n{answer}\n\nSources: {citations}",
        "ta": "ஆசிரியர் குறிப்புகளின்படி:\n\n{answer}\n\nஆதாரங்கள்: {citations}",
        "ta_latn": "Teacher notes pathi:\n\n{answer}\n\nSources: {citations}",
    },
    "rag_search_error": {
        "en": (
            "Sorry — I couldn't search the tutor notes right now. "
            "Please try again in a moment or ask your tutor directly."
        ),
        "si": "සමාවන්න — දැන් tutor notes search කරන්න බැරි වුණා. මොහොතකින් ආයෙත් උත්සාහ කරන්න, නැත්නම් ගුරුවරයාගෙන් අහන්න.",
        "si_latn": (
            "Sorry — dhan tutor notes search karanna bari una. "
            "Mohothakin ayeth try karanna, nathnam guruthumyagen ahanna."
        ),
        "ta": "மன்னிக்கவும் — இப்போது குறிப்புகளைத் தேட முடியவில்லை. சற்று நேரம் கழித்து முயலுங்கள் அல்லது ஆசிரியரிடம் கேளுங்கள்.",
        "ta_latn": "Sorry — ippo notes search panna mudiyala. Konjam neram kalichu try pannunga.",
    },
}


def t(key: str, language: str | None = None, **kwargs: object) -> str:
    """Look up a canned string; fall back to parent locale, then English."""
    lang = normalize_canned_language(language)
    catalog = STRINGS.get(key) or {}
    template = catalog.get(lang) or catalog.get(canned_language_parent(lang)) or catalog.get("en") or key
    if not kwargs:
        return template
    return template.format(**{name: "" if value is None else value for name, value in kwargs.items()})
