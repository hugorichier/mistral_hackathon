import getpass
import os
from langchain_mistralai import ChatMistralAI
from mistralan.chains.extractor import get_extractor
from mistralan.chains.event_extractor import get_event_extractor
from mistralan.chains.states_extractor import get_states_extractor
from mistralan.schemas import ConversationChunk, ConversationInfo
from datetime import date

os.environ["MISTRAL_API_KEY"] = ""

message = """**Therapist**: How are you doing today?

**Patient**: I’m... not sure, to be honest. I feel kind of off. I’ve been having a hard time getting out of bed lately.

**Therapist**: I see. When you say you feel "off," what do you mean? Is it a physical feeling, or more emotional?

**Patient**: It’s more emotional, I think. I just feel like there’s this constant heaviness, like a weight I can’t shake. It's hard to explain.

**Therapist**: That sounds difficult. How long have you been feeling this way?

**Patient**: Maybe a couple of months? I don’t know. It feels like it's been longer, but I didn’t really notice it until recently.

**Therapist**: What do you think might have triggered this feeling? Can you recall any specific events or changes around that time?

**Patient**: Well, I lost my job about three months ago, and things have been really hard since then. I thought I was handling it okay, but I guess... maybe I'm not?

**Therapist**: Losing a job can be a huge stressor. It makes sense that you’d feel a range of emotions about it. How did you feel when it first happened?

**Patient**: At first, I was just angry. It felt so unfair. I’d been at that company for years, and suddenly I was just... gone. But now, I don’t know. I feel more... numb? It’s like I don’t care about anything anymore.

**Therapist**: Numbness can sometimes be a way our mind tries to protect us from overwhelming emotions. Do you feel that numbness in other areas of your life, too?

**Patient**: Yeah, actually. I used to be excited about small things, like meeting friends or going to the gym. Now, it’s like I don’t even have the energy to try.

**Therapist**: It sounds like this sense of heaviness and numbness is affecting many areas of your life. How has it been impacting your relationships?

**Patient**: I’ve kind of pulled away from people. My friends invite me to things, but I always find an excuse not to go. I just don’t feel like I can be around people right now.

**Therapist**: Have any of your friends noticed this change in you? Have they reached out?

**Patient**: A couple of them have. One friend texted me the other day, asking if I was okay because I’ve been "off the grid." I didn’t really know what to say, so I just said I was busy.

**Therapist**: It sounds like you're feeling disconnected, both from yourself and others. Do you think talking to someone—like your friends—about what you're going through might help?

**Patient**: Maybe. But I don’t want to burden anyone with my problems, you know?

**Therapist**: I understand that feeling, but sometimes sharing what we’re going through can help ease that weight, even if it’s just a little. Do you think there’s a fear of how they might respond?

**Patient**: Yeah, a little. I don’t want them to think I’m falling apart. I’ve always been the strong one in the group. It's hard to let them see me like this.

**Therapist**: It sounds like you're putting a lot of pressure on yourself to maintain that image of strength. But strength can look different in different situations. Sometimes, reaching out for help can be one of the strongest things we do.

**Patient**: I’ve never thought about it that way. I guess I’ve always felt like I had to handle everything on my own.

**Therapist**: That’s a common feeling, but it's important to remember that you don’t have to carry everything by yourself. What would it be like to let others in, even just a little?

**Patient**: I don’t know... I guess it could help. But it’s scary. I don’t want them to see me as weak.

**Therapist**: I hear that. There’s a lot of vulnerability in opening up, especially when you've always been the one others rely on. But vulnerability isn’t a weakness—it’s a part of being human. What’s one small step you could take toward sharing what you're going through?

**Patient**: Maybe I could reach out to that friend who texted me. She’s been through tough stuff before, so maybe she’ll understand.

**Therapist**: That sounds like a really good first step. How would it feel to let her know you’ve been struggling and that you’re not feeling yourself?

**Patient**: I think it would feel... a little relieving, actually. Just admitting it out loud.

**Therapist**: That relief is important. You deserve to feel supported, and it’s okay to ask for help when you need it. Let's explore how you can approach that conversation, if you feel ready.

**Patient**: Yeah, I think I’d like that."""

llm = ChatMistralAI(model="mistral-large-latest")

event_extractor = get_event_extractor(llm)
state_extractor = get_states_extractor(llm)
runnable = get_extractor(event_extractor=event_extractor, state_extractor=state_extractor)

# Create an Input instance

chunk = ConversationChunk(
    info=ConversationInfo(
        id="0",
        patient_name='RoBERTo',
        patient_id="0",
        date=date.today()
    ),
    content=message,
    ts=0
)

input = {"chunk": chunk}

# Run the Runnable with the Input
results = runnable.invoke(input)

print(results)