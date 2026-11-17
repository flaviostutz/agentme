# Neurodivergence & Cognitive Profile Exploration
## Product, Scientific and Technical Specification


*Version:* 2.0
*Status:* Product concept and architecture defined; implementation planning
pending
*Audience:* Developers, product designers, researchers and domain experts
*Primary objective:* Build an adaptive, scientifically traceable
self-exploration system.

*Source email:* “Questionaire 2”  
*From:* Flávio Stutz <flaviostutz@gmail.com>  
*To:* Flávio Stutz <flaviostutz@gmail.com>  
*Date:* Mon, Nov 16, 2026 at 9:42 AM  
*Messages:* 1
---
## 1. Product vision
### 1.1 Objective

Build a self-exploration experience that helps people understand and
reflect on their cognitive, behavioral, emotional, sensory, social and
learning characteristics.

The system should behave like an investigation rather than a traditional
questionnaire.

It should start with broad questions, identify potentially interesting
experiences, and progressively ask more specific questions when the answers
justify further exploration.

At the end, the system presents patterns in the person’s answers, possible
connections with documented cognitive and neurodevelopmental profiles,
educational material and practical suggestions.

The system is NOT intended to:

   - Diagnose medical or psychological conditions.
   - Establish the probability that a person has a condition.
   - Replace professional assessment.
   - Classify people into mutually exclusive categories.
   - Claim that an individual characteristic is specific to one condition.

### 1.2 User experience

The intended experience:

   1. The person starts answering broad questions about everyday
   experiences.
   2. Their answers reveal characteristics worth exploring.
   3. The system activates relevant investigations.
   4. More specific questions explore those characteristics.
   5. Differentiation questions investigate different possible explanations
   for similar experiences.
   6. The system stops asking questions when additional information is
   unlikely to materially improve the exploration.
   7. The final result presents patterns, possible connections, strengths,
   challenges, uncertainties and suggestions for further exploration.

The user should not need to understand medical terminology or know which
conditions they want to investigate.

The system should discover relevant exploration paths from their answers.
### 1.3 Guiding principles

   - *Exploration, not diagnosis:* Never present results as a diagnosis or
   clinical screening outcome.
   - *Experience-led investigation:* Questions should explore experiences,
   not ask whether someone has a condition.
   - *Scientific traceability:* Published questions must have documented
   provenance and rationale.
   - *Neutral language:* Do not assume that a characteristic is a deficit.
   - *Strengths and challenges:* Explore both beneficial and challenging
   aspects.
   - *Context matters:* A characteristic may manifest differently across
   environments.
   - *Overlapping characteristics:* The same characteristic may be
   associated with several profiles.
   - *Adaptive questioning:* Ask only questions that are relevant to the
   person’s previous answers.
   - *Transparency:* Make evidence quality and uncertainty visible.
   - *No false precision:* Avoid diagnostic-looking scores and
   probabilities.
   - *Manageable duration:* The person should not need to answer hundreds
   of questions to explore a broad range of characteristics.

---
## 2. Conceptual model

The system has several distinct concepts.

| Concept | Description | Example |
| --- | --- | --- |
| Domain | Broad area of human experience | Attention |
| Characteristic | Individual tendency, experience or trait | Attention regulation |
| Question | A prompt that explores an experience | Difficulty sustaining attention on repetitive activities |
| Investigation | A structured exploration of one or more related characteristics | Attention regulation investigation |
| Profile | A documented cognitive or neurodevelopmental profile | ADHD |
| Instrument | Existing scientific questionnaire or assessment tool | Adult ADHD questionnaire |
| Source | Scientific publication or reference | Instrument validation study |
| Response | An answer provided by the user | Frequently |
| Evidence | Information collected from responses | Strong evidence of interest-dependent attention |

The relationship between these concepts is important:

   - Questions explore characteristics.
   - Investigations organize questions.
   - Characteristics may be associated with several profiles.
   - Scientific sources inform questions and characteristic definitions.
   - Responses provide evidence about characteristics.
   - The interpretation engine uses evidence to generate educational
   suggestions.

A profile must never be treated as the direct subject of an investigation
branch.

For example, the system should investigate attention regulation rather than
start an ADHD investigation.
---
## 3. Profiles and areas of exploration
### 3.1 Initial profiles

The initial catalogue should consider the following.
*Neurodevelopmental profiles*

   - ADHD
   - Autism
   - Dyslexia
   - Dyscalculia
   - Developmental Coordination Disorder (DCD / Dyspraxia)
   - Developmental Language Disorder (DLD)
   - Tourette syndrome

*Cognitive profiles*

   - Giftedness / high intellectual ability
   - Twice-exceptionality (2e), such as giftedness combined with ADHD or
   autism

*Other profiles and areas for future exploration*

   - Sensory processing differences
   - Synesthesia
   - Intellectual disability and adaptive functioning differences
   - Fetal Alcohol Spectrum Disorder (FASD)
   - Other neurological or developmental differences where appropriate
   scientific evidence exists

Not every item in this list is universally classified as neurodivergence.
The application should distinguish between neurodevelopmental conditions,
cognitive profiles, neurological differences and broader experiential
concepts.

Do not assume that every profile belongs in the first release.
### 3.2 Giftedness

Giftedness should be represented as a cognitive profile, not a medical
diagnosis.

There is no universally accepted self-report questionnaire that establishes
giftedness.

The system can explore characteristics such as:

   - Rapid learning and comprehension.
   - Abstract reasoning.
   - Intellectual curiosity.
   - Complex problem-solving.
   - Systems thinking.
   - Divergent thinking.
   - Need for intellectual stimulation.
   - Asynchronous development.
   - Existential interests.

These characteristics must not be used to claim that someone is gifted.
### 3.3 Twice-exceptionality

Twice-exceptionality (2e) refers to the coexistence of giftedness with one
or more other conditions or learning differences.

Represent this as an intersection or combination of profiles rather than as
an independent diagnosis.
### 3.4 Neurotypicality

Do not model neurotypicality as a parallel condition or profile score.

A low level of overlap with the profiles represented in the system does not
establish that a person is neurotypical.

The system should simply report when it has not identified strong patterns
within its current scope.
---
## 4. Adaptive investigation architecture

This is the central architectural feature of the product.

The system should not present a fixed list of questions.

Instead, it should use a graph-based investigation engine.
### 4.1 Progressive investigation

Questions should be organized into three main levels.
*Level 1 — Discovery*

Broad questions that explore everyday experiences across multiple domains.

Purpose:

   - Identify potentially relevant characteristics.
   - Discover which areas deserve further exploration.
   - Avoid introducing diagnostic terminology.
   - Keep the initial experience short.

Example:

“Do you find that your ability to concentrate changes significantly
depending on the activity?”
*Level 2 — Exploration*

More specific questions activated by responses to discovery questions.

Purpose:

   - Understand the nature of the experience.
   - Explore frequency and intensity.
   - Understand contexts.
   - Identify related characteristics.

Example:

“When an activity interests you, can you concentrate on it for much longer
than you originally intended?”
*Level 3 — Differentiation*

Questions that explore different possible mechanisms or explanations for
similar experiences.

Purpose:

   - Reduce ambiguity.
   - Understand contextual differences.
   - Identify overlapping characteristics.
   - Prevent premature conclusions.

Example:

“When you find it difficult to switch tasks, is it because you are deeply
absorbed in what you are doing, because interruptions are uncomfortable, or
because your attention has already moved elsewhere?”

These three levels are conceptual. An investigation may move between them
more than once.
### 4.2 Graph-based question flow

Questions are nodes.

Routing rules are directed edges.

A question can:

   - Lead to another question.
   - Activate one investigation.
   - Activate multiple investigations.
   - Activate a specific follow-up question.
   - Close an investigation.
   - Leave a characteristic unresolved.

The graph must support converging paths and reusable questions.

It must not be implemented as a strict tree.

For example, task switching may be relevant to attention regulation,
executive functioning and preference for predictability.

The system must be able to investigate more than one possible connection
without assuming that only one explanation is correct.
### 4.3 Example investigation flow

Discovery: General attention
        |
        +-- Experience frequently reported
        |       |
        |       +-- Explore sustained attention
        |       |
        |       +-- Explore interest-dependent attention
        |       |
        |       +-- Explore task switching
        |               |
        |               +-- Differentiate possible mechanisms
        |
        +-- Experience rarely reported
                |
                +-- Ask a balancing question if relevant
                |
                +-- Close or defer this branch

The system should be able to reactivate an investigation if later answers
provide new evidence.
### 4.4 Why this is not a profile-led questionnaire

Do not create primary branches such as:

   - ADHD investigation
   - Autism investigation
   - Giftedness investigation

Instead, create investigations around experiences:

   - Attention regulation
   - Executive functioning
   - Sensory processing
   - Social communication
   - Emotional regulation
   - Learning patterns
   - Intellectual characteristics
   - Motor coordination
   - Language processing

A single investigation may contribute evidence to several profiles.

This separation is fundamental to reducing confirmation bias.
---
## 5. Question types

The system should distinguish four question purposes.
### 5.1 Discovery questions

Broad entry questions.

Example:

“Do you experience differences in how easily you concentrate depending on
what you are doing?”
### 5.2 Exploration questions

Investigate a specific experience.

Example:

“When an activity interests you, can you concentrate on it for much longer
than you intended?”
### 5.3 Differentiation questions

Explore different possible explanations.

Example:

“When you remain focused on something, is it because you find it difficult
to disengage, because you enjoy it, or because you want to understand it
completely?”
### 5.4 Balancing questions

Explore counterexamples and experiences that may qualify an emerging
pattern.

Example:

“Are there situations in which you can easily stop an activity, even when
you find it interesting?”

Balancing questions are important to prevent the engine from only
confirming its initial hypotheses.
---
## 6. Investigation model

An investigation organizes a set of related questions and characteristics.

It is not a profile or diagnosis.
### 6.1 Investigation definition

Example:

{
  "investigation_id": "INV-ATTENTION",
  "name": "Attention regulation",
  "description": "Explore how attention is directed, sustained and shifted.",
  "domain_id": "attention",
  "entry_question_ids": [
    "Q-ATT-001"
  ],
  "characteristic_ids": [
    "attention_regulation",
    "sustained_attention",
    "task_switching",
    "interest_driven_attention"
  ],
  "question_budget": {
    "minimum": 1,
    "maximum": 8
  },
  "completion_rules": {
    "stop_when_sufficient": true,
    "allow_uncertainty": true
  }
}

### 6.2 Investigation fields

| Field | Description |
| --- | --- |
| `investigation_id` | Stable unique ID |
| `name` | Human-readable name |
| `description` | Purpose |
| `domain_id` | Main domain |
| `entry_question_ids` | Questions that can activate the investigation |
| `characteristic_ids` | Characteristics explored |
| `question_budget` | Limits for exploration |
| `completion_rules` | Conditions for stopping |
| `version` | Investigation version |
| `active` | Whether the investigation is available |

### 6.3 Investigation status

For a questionnaire session, each investigation should have a state.

Suggested statuses:

   - not_started
   - eligible
   - active
   - sufficient_evidence
   - completed
   - deferred
   - insufficient_evidence
   - skipped

Do not treat skipped or insufficient_evidence as negative evidence.
### 6.4 Investigation state example

{
  "investigation_id": "INV-ATTENTION",
  "status": "active",
  "characteristic_states": {
    "attention_regulation": {
      "evidence_strength": "moderate",
      "coverage": "partial",
      "uncertainty": "high"
    },
    "sustained_attention": {
      "evidence_strength": "strong",
      "coverage": "good",
      "uncertainty": "moderate"
    }
  },
  "questions_answered": 3,
  "questions_remaining": 5
}

Investigation state is specific to a user’s questionnaire session.
---
## 7. Question model
### 7.1 Question structure

The question is the central content entity.

Each question contains:

   - Stable ID.
   - Text.
   - Domain.
   - Question type.
   - Characteristic associations.
   - Response scale.
   - Scientific provenance.
   - Routing rules.
   - Validation status.
   - Version information.

Scientific provenance is embedded directly inside sources[].

A separate question-source mapping collection is not required in the
initial implementation.
### 7.2 Example question

{
  "question_id": "Q-ATT-001",
  "text": "Do you find it easier to concentrate on activities that
genuinely interest you than on activities that feel repetitive or
uninteresting?",
  "domain_id": "attention",
  "question_type": "discovery",
  "characteristic_ids": [
    "attention_regulation",
    "interest_driven_attention"
  ],
  "response_scale": {
    "type": "frequency",
    "scale_id": "FREQUENCY_8"
  },
  "sources": [
    {
      "source_id": "SRC-EXAMPLE-001",
      "instrument_id": "INST-EXAMPLE-001",
      "construct": "attention regulation",
      "relationship": "construct_based",
      "adaptation_type": "independently_authored",
      "reference_location": null,
      "evidence_note": "Independently written to explore the construct
described by the referenced instrument."
    }
  ],
  "routing": {
    "rules": [
      {
        "condition": {
          "operator": "greater_than_or_equal",
          "value": 4
        },
        "action": "activate_investigation",
        "target_id": "INV-SUSTAINED-ATTENTION"
      }
    ]
  },
  "validation_status": "unvalidated",
  "version": "1.0",
  "active": true
}

Example source IDs are placeholders and must not be treated as verified
scientific references.
### 7.3 Embedded scientific provenance

Each sources[] element should contain:

| Field | Description |
| --- | --- |
| `source_id` | Scientific publication reference |
| `instrument_id` | Instrument reference, optional |
| `construct` | Construct or subscale informing the question |
| `relationship` | How the question relates to the source |
| `adaptation_type` | Original item, authorized adaptation, independently authored or exploratory |
| `reference_location` | Original item number, subscale, page or section |
| `evidence_note` | Rationale explaining the relationship |

A question can have multiple sources.

A source can be referenced by multiple questions.

Do not duplicate bibliographic metadata inside the question.
### 7.4 Provenance relationship types

   - item_adapted
   - construct_based
   - subscale_based
   - literature_based
   - cross_instrument
   - exploratory

### 7.5 Adaptation types

   - original_instrument_item
   - authorized_adaptation
   - independently_authored
   - exploratory

### 7.6 Question validation statuses

   - draft
   - unvalidated
   - expert_review
   - pilot_tested
   - validated_for_exploratory_use
   - rejected
   - deprecated

A question does not inherit validation from its source instrument.
---
## 8. Routing model
### 8.1 Routing responsibility

Routing determines what should be investigated next.

Avoid scattering hardcoded conditional logic across the application.

All routing should be evaluated through a central routing engine.
### 8.2 Routing actions

Suggested actions:

| Action | Meaning |
| --- | --- |
| `continue_to` | Ask another question |
| `activate_investigation` | Start an investigation |
| `activate_question` | Add a question to the active queue |
| `complete_investigation` | Close an investigation |
| `skip_investigation` | Mark an investigation as not currently relevant |
| `review_characteristic` | Collect additional evidence about a characteristic |

One answer may trigger multiple actions.
### 8.3 Routing conditions

Support conditions such as:

   - Answer greater than or equal to a value.
   - Answer less than a value.
   - Answer within a range.
   - Multiple answers satisfy a condition.
   - A characteristic has insufficient evidence.
   - An investigation is active.
   - A balancing question is required.
   - A question has already been answered.

Do not implement arbitrary executable code in JSON configuration.

Use a defined condition language and validate it against a schema.
### 8.4 Example routing

{
  "rules": [
    {
      "rule_id": "ROUTE-001",
      "priority": 10,
      "condition": {
        "operator": "greater_than_or_equal",
        "value": 4
      },
      "actions": [
        {
          "type": "activate_investigation",
          "target_id": "INV-SUSTAINED-ATTENTION"
        },
        {
          "type": "activate_investigation",
          "target_id": "INV-INTEREST-DRIVEN-ATTENTION"
        }
      ]
    }
  ]
}

The threshold is illustrative. Actual routing thresholds must be selected
through pilot testing and should not be represented as clinical cutoffs.
### 8.5 Routing safeguards

   - Never activate an investigation solely because a profile is suspected.
   - Never permanently exclude a characteristic based on one answer.
   - Avoid repeatedly activating completed investigations.
   - Prevent circular question loops.
   - Do not ask the same question twice in a session unless explicitly
   intended.
   - Preserve unanswered, skipped and not-applicable states.
   - Allow multiple investigations to remain active.
   - Support deferred investigations that may be reactivated later.

---
## 9. Investigation engine

The investigation engine is responsible for deciding which question should
be presented next.

It should operate using the current questionnaire session state.
### 9.1 Evidence-driven question selection

Consider:

   1. Relevance to active investigations.
   2. Characteristics with incomplete coverage.
   3. Uncertainty that can be reduced by another question.
   4. Need for differentiation.
   5. Need for balancing evidence.
   6. Question priority.
   7. Question budget.
   8. Whether the question has already been answered.

A question should only be selected when it has meaningful potential to
improve the exploration.
### 9.2 Evidence state

For each characteristic, maintain separate dimensions:

   - Positive evidence.
   - Counter-evidence.
   - Evidence coverage.
   - Consistency.
   - Context stability.
   - Impact.
   - Uncertainty.

Do not collapse these into one number prematurely.

Example:

{
  "characteristic_id": "attention_regulation",
  "positive_evidence": "strong",
  "counter_evidence": "moderate",
  "coverage": "partial",
  "consistency": "moderate",
  "context_stability": "low",
  "impact": "both_beneficial_and_challenging",
  "uncertainty": "moderate"
}

These are illustrative qualitative states.
### 9.3 Question value

The engine should prioritize questions that can materially improve
understanding.

Potential question-selection considerations:

   - Does the question explore an unexamined characteristic?
   - Does it distinguish between competing explanations?
   - Does it provide balancing evidence?
   - Does it clarify context or impact?
   - Has the characteristic already been explored sufficiently?
   - Would another question add meaningful information?

An advanced implementation may use information-gain or
uncertainty-reduction calculations, but the first version should use
transparent rules.

Do not introduce machine learning or an opaque AI decision-maker for
initial routing.
### 9.4 Stopping conditions

An investigation can stop when:

   - Its relevant characteristics have adequate exploratory coverage.
   - Additional questions are unlikely to improve interpretation.
   - The question budget has been reached.
   - The user chooses to stop.
   - The investigation is not currently relevant.
   - The remaining uncertainty cannot reasonably be resolved through
   available questions.

Stopping an investigation does not imply that a characteristic or profile
is absent.
### 9.5 Reactivation

An investigation may be reactivated if later answers provide new relevant
evidence.

For example, a user may initially report few attention difficulties but
later describe difficulties with task switching in a particular context.

The engine should be able to revisit attention regulation without
restarting the entire investigation.
---
## 10. Question budget and questionnaire duration

The main objective is to keep the experience manageable even when the
underlying catalogue contains hundreds of questions.

Initial design targets:

| Question type | Initial target |
| --- | --- |
| Discovery questions | 12–16 |
| Exploration questions | 8–15 |
| Differentiation questions | 4–8 |
| Typical total | 24–39 |
| Hard maximum | 45–50 |

These are product-design targets, not scientifically established limits.

The question budget should be configurable.

The system should support:

   - A total session budget.
   - A per-investigation budget.
   - A maximum number of consecutive questions from one domain.
   - Optional user-controlled exploration depth.
   - Early completion when evidence is sufficient.
   - Explicit user control to stop or skip.

A person should not be forced to answer all questions in the catalogue.
---
## 11. Response model
### 11.1 Frequency scale

| Value | Label |
| --- | --- |
| 0 | Never |
| 1 | Very rarely |
| 2 | Rarely |
| 3 | Occasionally |
| 4 | Sometimes |
| 5 | Frequently |
| 6 | Very frequently |
| 7 | Almost always |

### 11.2 Agreement scale

| Value | Label |
| --- | --- |
| 0 | Strongly disagree |
| 1 | Disagree |
| 2 | Somewhat disagree |
| 3 | Slightly disagree |
| 4 | Slightly agree |
| 5 | Somewhat agree |
| 6 | Agree |
| 7 | Strongly agree |

### 11.3 Non-numerical answers

   - Not sure.
   - Cannot assess.
   - Not applicable.
   - Prefer not to answer.

These must not be treated as zero or as evidence against a characteristic.
### 11.4 Experience, context and impact

Separate three dimensions where appropriate:

   1. Experience: how frequently or strongly does it occur?
   2. Context: in which situations does it occur?
   3. Impact: how does it affect the person?

Suggested impact options:

   - Mostly beneficial.
   - Mostly neutral.
   - Occasionally challenging.
   - Frequently challenging.
   - Both beneficial and challenging.
   - Varies significantly by context.

Suggested contexts:

   - Most situations.
   - Work or study.
   - Social situations.
   - Personal projects and interests.
   - Under stress or pressure.
   - Specific environments.
   - Varies.

Do not collect unnecessary metadata for every question.
### 11.5 Response entity

{
  "response_id": "RESP-001",
  "session_id": "SESSION-001",
  "question_id": "Q-ATT-001",
  "question_version": "1.0",
  "answer": 6,
  "context": [
    "work",
    "personal_projects"
  ],
  "impact": "both_beneficial_and_challenging",
  "notes": null,
  "answered_at": "2026-11-16T12:00:00Z"
}

Preserve the question version for historical interpretation.
---
## 12. Questionnaire session

A session represents one complete or partial self-exploration experience.

Example:

{
  "session_id": "SESSION-001",
  "questionnaire_version": "1.0",
  "status": "in_progress",
  "started_at": "2026-11-16T12:00:00Z",
  "completed_at": null,
  "question_budget": {
    "maximum": 45,
    "used": 12
  },
  "active_investigation_ids": [
    "INV-ATTENTION",
    "INV-SENSORY"
  ],
  "completed_investigation_ids": [],
  "deferred_investigation_ids": [],
  "response_ids": [
    "RESP-001"
  ]
}

Suggested session statuses:

   - not_started
   - in_progress
   - paused
   - completed
   - abandoned

A session must retain enough information to resume an investigation without
repeating questions unnecessarily.
---
## 13. Domains and initial investigation catalogue

The initial questionnaire should cover eight domains.

| Domain ID | Domain |
| --- | --- |
| `attention` | Attention, concentration and mental activity |
| `executive_function` | Executive function and cognitive processing |
| `sensory_processing` | Sensory processing and physical regulation |
| `social_communication` | Social interaction and communication |
| `thinking_patterns` | Thinking patterns and intellectual characteristics |
| `emotional_experience` | Emotional experience and regulation |
| `interests_learning` | Interests, motivation and learning |
| `adaptation_environment` | Adaptation, routines and environment |

Potential investigation catalogue:
*Attention*

   - Attention regulation
   - Sustained attention
   - Interest-driven attention
   - Task switching
   - Mental activity
   - Hyperfocus and intense immersion

*Executive functioning*

   - Working memory
   - Planning and organization
   - Initiation and task completion
   - Impulse control
   - Time perception
   - Cognitive flexibility

*Sensory processing*

   - Auditory sensitivity
   - Visual sensitivity
   - Tactile sensitivity
   - Sensory seeking
   - Sensory avoidance
   - Interoception
   - Repetitive self-regulation

*Social communication*

   - Interpretation of social cues
   - Direct versus implicit communication
   - Conversation timing
   - Shared-interest interaction
   - Social recovery and solitude
   - Precision in language

*Thinking patterns*

   - Pattern recognition
   - Abstract reasoning
   - Systems thinking
   - Divergent thinking
   - Cross-domain connections
   - Metaphorical and symbolic thinking
   - Anticipatory reasoning

*Emotional experience*

   - Emotional intensity
   - Emotional regulation
   - Rejection sensitivity
   - Alexithymia-related experiences
   - Fairness and justice sensitivity
   - Existential concerns

*Interests and learning*

   - Breadth of interests
   - Depth of interests
   - Curiosity-driven learning
   - Rapid comprehension
   - Need for complexity
   - Independent exploration
   - Learning preferences

*Adaptation and environment*

   - Need for predictability
   - Response to transitions
   - Response to unexpected changes
   - Asynchronous development
   - Environmental fit
   - Intellectual stimulation needs

This is an initial catalogue, not a fixed or exhaustive list.
---
## 14. Initial question bank

The previously drafted 48 questions should be retained as an initial
question inventory.

They should not be treated as a fixed sequence.

The questions should be classified as discovery, exploration,
differentiation or balancing questions.

The initial inventory is:
*Attention*

   1. Do you find it difficult to maintain concentration on activities that
   do not interest you, even when they are important?
   2. When deeply involved in an activity, do you sometimes lose track of
   time, your surroundings or other responsibilities?
   3. Do you frequently seek novelty, variety or intellectual stimulation?
   4. Does your mind tend to remain active, moving between thoughts, ideas
   or possible scenarios?
   5. Are there particular subjects or activities in which you can
   concentrate intensely for long periods?
   6. Do you often understand new concepts quickly, sometimes grasping the
   overall idea before all intermediate steps have been explained?

*Executive functioning*

   7. Do you find it difficult to organize, prioritize, plan or complete
   tasks, even when you understand what needs to be done?
   8. Do you sometimes forget recently received information, lose track of
   instructions or struggle to hold several pieces of information in mind?
   9. Do you find it difficult to switch between tasks or adapt when you
   need to change what you are doing?
   10. Do you sometimes act, speak or respond before having time to
   consider the consequences?
   11. Do you sometimes understand something intellectually but find it
   difficult to organize, communicate or execute what you know?
   12. Do you prefer to understand the overall picture or underlying
   concept before learning individual steps?

*Sensory processing*

   13. Do sounds, lights, textures, smells, tastes or other sensory
   experiences affect you more or less strongly than they seem to affect other
   people?
   14. Do you use movement, fidgeting, tapping, pacing or repetitive sounds
   to help yourself concentrate or regulate your state?
   15. Do you often feel physically or mentally restless, even when you
   would prefer to relax?
   16. Do you sometimes have difficulty recognizing internal physical
   signals such as hunger, thirst, tiredness, temperature or the need to use
   the bathroom?
   17. Do you sometimes have difficulty identifying or describing what
   emotion you are experiencing?
   18. Do repetitive movements, sounds, thoughts or routines help you feel
   comfortable, focused or regulated?

*Social communication*

   19. Do you sometimes find it difficult to interpret social cues,
   conversational expectations or nonverbal communication?
   20. Do you prefer people to communicate directly and explicitly rather
   than relying on hints, implications or ambiguity?
   21. Do you find it easier to connect with people through shared
   interests or intellectual discussions than through conventional social
   interaction?
   22. Do you sometimes interrupt, respond too quickly or find it difficult
   to judge when to speak in a conversation?
   23. Do you often value precision in language and feel a need to correct
   or clarify statements that seem inaccurate or ambiguous?
   24. Do you often prefer spending time alone to process information,
   recover from interaction or explore your thoughts?

*Thinking patterns*

   25. Do you frequently notice patterns, structures, relationships or
   details that other people seem to overlook?
   26. Do you naturally connect ideas from different subjects or areas of
   knowledge?
   27. Do you tend to think in terms of systems, models or abstract
   structures involving many interconnected elements?
   28. Do you frequently explore theoretical, philosophical or existential
   questions?
   29. Do you naturally think through metaphors, symbols, analogies or
   abstract representations?
   30. Do you often anticipate consequences, problems or possible scenarios
   before they become obvious to others?

*Emotional experience*

   31. Do you experience emotions intensely, sometimes finding it difficult
   to regulate their intensity?
   32. Do criticism, rejection, exclusion or the possibility of
   disappointing someone affect you particularly strongly?
   33. Do you have strong reactions to perceived unfairness, injustice,
   inconsistency or violations of principles?
   34. Did you experience emotional or existential concerns earlier or more
   intensely than people around you seemed to?
   35. Do you sometimes experience a strong emotional reaction before
   understanding what triggered it?
   36. Do you tend to seek underlying reasons, implications or complexity
   rather than accepting superficial explanations?

*Interests and learning*

   37. Do you have a wide range of interests and frequently explore new
   subjects?
   38. Do you sometimes become deeply absorbed in a small number of
   subjects for extended periods?
   39. Are you particularly motivated by challenging, complex or
   intellectually stimulating activities?
   40. Do you frequently pursue knowledge out of curiosity, even when there
   is no immediate practical benefit?
   41. Do you prefer understanding underlying principles rather than
   memorizing facts or following instructions without explanation?
   42. Do you prefer exploring, experimenting and investigating
   independently rather than following a predetermined learning structure?

*Adaptation and environment*

   43. Do routines, predictability and clear expectations help you feel
   comfortable and function effectively?
   44. Do unexpected changes, interruptions or transitions cause
   discomfort, frustration or difficulty reorganizing your activities?
   45. Have you experienced uneven development across intellectual,
   emotional, social or practical skills?
   46. Do you sometimes feel that your way of thinking, learning or
   communicating differs from what your environment expects?
   47. Do you sometimes respond particularly effectively in emergencies or
   situations requiring quick decisions?
   48. Do you often feel that your environment does not provide enough
   complexity, depth or intellectual challenge?

These questions need review and scientific mapping before publication. Some
may be split, rewritten or removed.
---
## 15. Scientific foundation and source catalogue
### 15.1 Purpose

The scientific catalogue provides provenance for questions and
characteristic definitions.

It is not intended to turn the product into a diagnostic instrument.

Questions should be independently authored in accessible language, informed
by documented scientific constructs.
### 15.2 Initial instruments to investigate

| Area | Candidate instrument or reference | Limitation to investigate |
| --- | --- | --- |
| Dyslexia | Adult Reading History Questionnaire (ARHQ) | Reading history and reading difficulties; population applicability |
| Dyslexia | Dyslexia Adult Checklist (DAC) | Verify current validation and licensing |
| Dyscalculia | Colorado Learning Difficulties Questionnaire (CLDQ) | Primarily child/adolescent research |
| Dyscalculia | dCALQ | Acquired acalculia is not developmental dyscalculia |
| DCD | Adult DCD / Dyspraxia Checklist | Verify validation evidence |
| DCD | Adolescents and Adults Coordination Questionnaire (AAC-Q) | Review psychometric limitations |
| Sensory processing | Adolescent/Adult Sensory Profile | Sensory patterns, not a specific diagnosis |
| Sensory processing | Glasgow Sensory Questionnaire (GSQ) | Sensory sensitivity research |
| Tourette | Yale Global Tic Severity Scale (YGTSS) | Clinician-rated |
| Tourette | Premonitory Urge for Tics Scale (PUTS) | Focused on premonitory urges |
| Adaptive functioning | Vineland Adaptive Behavior Scales | Structured assessment, not a simple self-report |
| DLD | Adult DLD research and clinical guidance | Adult evidence remains limited |
| Giftedness | Standardized cognitive assessment literature | No universally accepted self-report questionnaire establishes giftedness |
| ADHD | Established ADHD research and assessment instruments | Review population, licensing and purpose |
| Autism | Established autism research and assessment instruments | Review masking, population, validity and licensing |

This is a research starting point. Verify all references before relying on
them.
### 15.3 Verification requirements

For every source and instrument, record:

   - Exact title and version.
   - Authors.
   - Publication year.
   - DOI or stable URL.
   - Intended population.
   - Age range.
   - Construct measured.
   - Instrument type.
   - Psychometric evidence.
   - Validation population.
   - Limitations.
   - Licensing and adaptation rights.
   - Verification status.

An instrument does not automatically validate a question independently
written from its constructs.

Do not reproduce proprietary questionnaire items without permission.
---
## 16. Master data model

The initial architecture should use the following master catalogues:

   1. sources
   2. instruments
   3. characteristics
   4. profiles
   5. domains
   6. investigations
   7. questions

Session-specific data:

   8. sessions
   9. responses
   10. investigation_states
   11. results

### 16.1 Source

{
  "source_id": "SRC-ARHQ-2000",
  "title": "The Adult Reading History Questionnaire",
  "authors": ["Lefly", "Pennington"],
  "year": 2000,
  "doi": "10.1177/002221940003300306",
  "url": null,
  "source_type": "validation_study",
  "evidence_status": "to_be_verified",
  "notes": null
}

### 16.2 Instrument

{
  "instrument_id": "INST-ARHQ",
  "name": "Adult Reading History Questionnaire",
  "abbreviation": "ARHQ",
  "population": {
    "age_range": "adult",
    "population_notes": null
  },
  "purpose": "Explore reading history and reading-related difficulties.",
  "instrument_type": "self_report",
  "constructs": [
    "reading_history",
    "reading_fluency"
  ],
  "source_ids": [
    "SRC-ARHQ-2000"
  ],
  "validation_status": "published",
  "licensing": {
    "status": "to_be_verified",
    "notes": null
  },
  "limitations": []
}

### 16.3 Characteristic

{
  "characteristic_id": "attention_regulation",
  "name": "Attention regulation",
  "domain_id": "attention",
  "description": "Differences in directing, sustaining and shifting attention.",
  "profile_associations": [
    {
      "profile_id": "ADHD",
      "relationship": "documented_association",
      "evidence_status": "to_be_verified",
      "source_ids": [],
      "notes": null
    }
  ],
  "tags": [
    "attention",
    "cognition",
    "executive_function"
  ]
}

### 16.4 Profile

{
  "profile_id": "ADHD",
  "name": "Attention-Deficit/Hyperactivity Disorder",
  "category": "neurodevelopmental",
  "description": "A neurodevelopmental condition involving persistent
patterns of inattention and/or hyperactivity-impulsivity.",
  "exploration_enabled": true,
  "disclaimer": "This questionnaire cannot establish or rule out ADHD.",
  "source_ids": []
}

### 16.5 Characteristic association relationships

   - documented_association
   - commonly_discussed
   - possible_association
   - exploratory_association

Evidence status must be maintained separately.
---
## 17. Data architecture and relationships

Logical relationships:

   - A source may document multiple instruments.
   - An instrument may be supported by multiple sources.
   - A question may reference multiple sources and instruments.
   - A question may explore multiple characteristics.
   - An investigation may contain multiple questions.
   - A question may participate in multiple investigations.
   - An investigation may explore multiple characteristics.
   - A characteristic may be associated with multiple profiles.
   - A session contains multiple responses.
   - A session tracks multiple investigation states.
   - A result summarizes a session.

Question-to-source and question-to-characteristic mappings remain embedded
inside the question object.

Do not create separate mapping collections for these relationships in the
initial implementation.
### 17.1 Recommended project structure

```text
data/
|-- sources.json
|-- instruments.json
|-- characteristics.json
|-- profiles.json
|-- domains.json
|-- investigations/
|   |-- attention.json
|   |-- executive_function.json
|   |-- sensory_processing.json
|   |-- social_communication.json
|   |-- thinking_patterns.json
|   |-- emotional_experience.json
|   |-- interests_learning.json
|   `-- adaptation_environment.json
|-- questions/
|   |-- discovery.json
|   |-- exploration.json
|   |-- differentiation.json
|   `-- balancing.json
`-- questionnaire_config.json

schemas/
|-- source.schema.json
|-- instrument.schema.json
|-- characteristic.schema.json
|-- profile.schema.json
|-- domain.schema.json
|-- investigation.schema.json
|-- question.schema.json
|-- session.schema.json
|-- response.schema.json
|-- investigation_state.schema.json
`-- result.schema.json

engine/
|-- question_selector
|-- routing_evaluator
|-- investigation_manager
|-- evidence_aggregator
|-- stopping_evaluator
`-- interpretation_engine

user-data/
|-- sessions/
|-- responses/
`-- results/
```

The implementation may use another storage architecture if the existing
repository requires it. Keep the logical content model independent of
persistence technology.
---
## 18. Interpretation and results
### 18.1 Characteristic-level evidence

The primary interpretation unit is the characteristic.

For each characteristic, consider:

   - Positive evidence.
   - Counter-evidence.
   - Evidence coverage.
   - Consistency.
   - Context stability.
   - Impact.
   - Uncertainty.

Keep these dimensions separate.

A characteristic may be strongly present in one context and absent in
another.

Do not simply cancel positive and negative evidence.
### 18.2 Profile-level interpretation

Profiles are a secondary educational layer.

The interpretation engine may identify patterns of characteristics that
overlap with documented profile literature.

Do not:

   - Invent weights.
   - Treat characteristics as independent when they are not.
   - Assume shared characteristics are profile-specific.
   - Calculate diagnostic probabilities.
   - Display percentages that imply likelihood of diagnosis.
   - Infer that a profile is absent because a person did not endorse its
   associated characteristics.

Start with transparent rules.
### 18.3 Result example

{
  "result_id": "RESULT-001",
  "questionnaire_version": "1.0",
  "interpretation_version": "1.0",
  "generated_at": "2026-11-16T12:00:00Z",
  "characteristics": [
    {
      "characteristic_id": "attention_regulation",
      "evidence_strength": "strong",
      "consistency": "moderate",
      "contexts": [
        "work",
        "personal_projects"
      ],
      "impact": "both_beneficial_and_challenging",
      "explanation": "Your answers suggest that interest and task
characteristics influence your ability to sustain attention."
    }
  ],
  "exploration_suggestions": [
    {
      "profile_id": "ADHD",
      "reason": "Some of your responses overlap with experiences
discussed in ADHD literature.",
      "supporting_characteristic_ids": [
        "attention_regulation"
      ],
      "suggestion_type": "educational_exploration"
    }
  ],
  "limitations": [
    "This is an exploratory self-reflection result, not a clinical assessment."
  ]
}

### 18.4 Results experience

Present:

   1. Characteristics that stood out.
   2. Strengths and useful tendencies.
   3. Shared characteristics.
   4. Connections worth exploring.
   5. Context and impact.
   6. Uncertainties and areas not explored.
   7. Practical suggestions.
   8. Educational references.

Suggested language:

   - “Your answers suggest…”
   - “You may find it useful to explore…”
   - “Some of these experiences are discussed in…”
   - “This characteristic is shared across several profiles.”
   - “There is not enough information to draw a clear conclusion.”

Avoid diagnostic labels and probability scores.
---
## 19. Scientific and question validation

Validation must be separated into distinct stages.

   1. Source verification.
   2. Instrument validation review.
   3. Question provenance review.
   4. Question clarity and neutrality review.
   5. Questionnaire coverage and redundancy review.
   6. Exploratory usability testing.

Potential future activities:

   - Expert review.
   - Cognitive interviews.
   - Pilot testing.
   - Analysis of missing responses.
   - Test-retest reliability, where appropriate.
   - Construct validity research.
   - Evaluation across demographic and language groups.

Do not describe the questionnaire as scientifically validated until
appropriate studies have been completed.
### 19.1 Mandatory publication quality gate

A question cannot be published unless:

   - It has a stable ID.
   - It belongs to a valid domain.
   - It references at least one characteristic.
   - It has clear and neutral wording.
   - It has a valid response scale.
   - It has documented provenance or explicit exploratory rationale.
   - It has a validation status.
   - Relevant licensing restrictions have been considered.

---
## 20. Non-functional requirements
### 20.1 Maintainability

   - Stable IDs.
   - Independent question versioning.
   - Independent source and instrument versioning.
   - JSON Schema validation.
   - Referential integrity validation.
   - No hardcoded profile relationships in application logic.
   - Separation of content, presentation and interpretation.

### 20.2 Extensibility

Support:

   - New profiles.
   - New characteristics.
   - New domains.
   - New investigations.
   - New questions.
   - Multiple sources per question.
   - Multiple instruments per question.
   - Additional response types.
   - Multiple languages.
   - New routing rules.
   - New interpretation rules.

### 20.3 Internationalization

Support multiple languages in future.

Translations of scientific questionnaire items must not be assumed to
preserve psychometric properties.

Track translation provenance when relevant.
### 20.4 Privacy

Responses may contain sensitive personal information.

   - Collect only necessary information.
   - Avoid requiring personally identifying information.
   - Protect stored responses.
   - Avoid exposing responses in logs.
   - Provide retention and deletion policies.
   - Obtain informed consent where appropriate.
   - Do not share responses with third parties without explicit
   authorization.

---
## 21. Implementation roadmap

The implementation should prioritize the content foundation and adaptive
engine before building a large questionnaire.
*Phase 1 — Repository inspection and technical planning*

   - Inspect the existing repository.
   - Identify language, frameworks and architecture.
   - Identify existing persistence and validation patterns.
   - Identify tests and build pipelines.
   - Produce an implementation plan.
   - Avoid introducing unnecessary dependencies.

Deliverable: implementation plan and technical architecture.
*Phase 2 — Data foundation*

Create schemas for:

   - Source.
   - Instrument.
   - Characteristic.
   - Profile.
   - Domain.
   - Investigation.
   - Question.
   - Session.
   - Response.
   - Investigation state.
   - Result.

Implement:

   - ID validation.
   - Referential integrity.
   - Enumerated values.
   - Versioning.
   - JSON data validation.

Deliverable: validated content model.
*Phase 3 — Scientific catalogue*

   - Verify initial scientific references.
   - Populate sources.
   - Populate instruments.
   - Define constructs.
   - Populate characteristic definitions.
   - Review profile associations.
   - Record evidence and licensing status.

Deliverable: traceable scientific catalogue.
*Phase 4 — Investigation and question architecture*

   - Define investigation schema.
   - Define question schema.
   - Implement embedded sources[].
   - Implement question routing schema.
   - Implement condition evaluation.
   - Implement investigation state.
   - Implement cycle detection and duplicate prevention.
   - Implement question budgets and stopping rules.

Deliverable: working adaptive investigation engine without a user interface.
*Phase 5 — Initial content*

   - Import original characteristic CSV.
   - Verify its exact row count.
   - Normalize IDs and domains.
   - Retain original values.
   - Map the initial 48 questions.
   - Identify discovery questions.
   - Create exploration and differentiation questions.
   - Add balancing questions.
   - Add scientific provenance.

Deliverable: initial investigation catalogue.
*Phase 6 — Questionnaire experience*

   - Render the next question dynamically.
   - Save responses.
   - Show progress.
   - Support skipped questions.
   - Support pause and resume.
   - Support optional context and impact.
   - Show appropriate question navigation without exposing diagnostic
   labels.

Deliverable: usable adaptive questionnaire.
*Phase 7 — Evidence and interpretation*

   - Aggregate characteristic-level evidence.
   - Track coverage and uncertainty.
   - Support multiple simultaneous investigations.
   - Implement transparent stopping rules.
   - Implement profile associations.
   - Generate educational suggestions.

Deliverable: interpretation engine.
*Phase 8 — Results and educational content*

   - Characteristic summaries.
   - Strengths and challenges.
   - Possible connections.
   - Practical suggestions.
   - Educational references.
   - Limitations and disclaimers.

Deliverable: complete self-exploration experience.
*Phase 9 — Quality and validation*

   - Expert review.
   - User interviews.
   - Pilot testing.
   - Content review.
   - Accessibility review.
   - Privacy and security review.

Deliverable: release readiness assessment.
---
## 22. GitHub Copilot implementation instructions

Copilot should work incrementally.

Do not attempt to implement the entire application in one step.
*Initial instruction*

First inspect the existing repository and report:

   1. Current architecture.
   2. Language and framework.
   3. Existing data model.
   4. Existing test strategy.
   5. Recommended implementation approach.
   6. Dependencies that can be reused.
   7. Proposed implementation milestones.

Do not modify files before presenting the implementation plan.
### Development rules

   - Follow the existing project conventions.
   - Keep content separate from application logic.
   - Prefer configuration-driven routing.
   - Do not hardcode profile-led branching.
   - Do not implement diagnosis or probability calculations.
   - Use stable IDs.
   - Validate all content against schemas.
   - Preserve question and interpretation versions.
   - Add unit tests for routing and stopping behavior.
   - Add integration tests for complete investigation sessions.
   - Document all assumptions.
   - Do not invent scientific references.
   - Mark unverified content explicitly.

### Priority implementation tasks
#### Task 1 — Data schemas

Create and validate schemas for all master and session entities.
#### Task 2 — Content validation

Implement validation for:

   - Unique IDs.
   - Valid references.
   - Missing characteristic mappings.
   - Missing question provenance.
   - Invalid routing targets.
   - Circular routing.
   - Invalid response scales.
   - Deprecated content.

#### Task 3 — Investigation engine

Implement:

   - Session state.
   - Investigation activation.
   - Question selection.
   - Routing evaluation.
   - Multiple active investigations.
   - Question budgets.
   - Stopping conditions.
   - Investigation reactivation.

#### Task 4 — Engine tests

Test scenarios such as:

   - A broad question activates one investigation.
   - A question activates multiple investigations.
   - A differentiation question is selected when uncertainty is high.
   - A balancing question is selected after a strong initial pattern.
   - A completed question is not repeated.
   - A question cannot create an infinite routing loop.
   - An investigation stops when its budget is reached.
   - An investigation can be reactivated by later evidence.
   - Skipped and unanswered questions do not count as negative evidence.

#### Task 5 — Initial content

Import the existing characteristics and question inventory.

Map every question to characteristics and scientific provenance.
#### Task 6 — Questionnaire interface

Build a dynamic interface that requests the next question from the
investigation engine rather than rendering a predefined sequence.
#### Task 7 — Interpretation

Implement transparent characteristic-level evidence aggregation.
#### Task 8 — Results

Present patterns and educational suggestions without diagnosis-like
classifications.
---
## 23. Acceptance criteria for the first functional prototype

The first prototype should demonstrate the following end-to-end scenario:

   1. A user starts a questionnaire session.
   2. The system presents broad discovery questions from several domains.
   3. A response activates an investigation.
   4. The investigation selects relevant exploration questions.
   5. Further responses activate differentiation or balancing questions.
   6. Multiple investigations can remain active simultaneously.
   7. The system avoids repeating questions.
   8. The system respects a configurable question budget.
   9. An investigation can stop with insufficient evidence or sufficient
   exploratory evidence.
   10. Later answers can reactivate a previously deferred investigation.
   11. The engine aggregates evidence at characteristic level.
   12. The result shows possible connections with documented profiles.
   13. Every question can be traced to its characteristics and scientific
   sources.
   14. The result clearly communicates uncertainty and the non-diagnostic
   nature of the product.

The prototype does not need a sophisticated scoring algorithm or a complete
scientific catalogue.

The first milestone is to demonstrate that the investigation engine works
correctly with a small, carefully mapped set of questions.
---
## 24. Key architectural decisions

| Decision | Agreed direction |
| --- | --- |
| Product purpose | Self-exploration, not diagnosis |
| Initial population | Adults |
| Question flow | Adaptive, investigation-driven |
| Investigation structure | Graph-based |
| Question types | Discovery, exploration, differentiation, balancing |
| Primary interpretation unit | Characteristic |
| Investigation entry | Broad experience-based questions |
| Profile-led branching | Not allowed |
| Simultaneous investigations | Supported |
| Question reuse | Supported |
| Question selection | Central engine |
| Routing rules | Embedded in question |
| Scientific provenance | Embedded sources[] |
| Separate question-source mapping | Not required initially |
| Source catalogue | Separate master catalogue |
| Instrument catalogue | Separate master catalogue |
| Characteristic catalogue | Separate master catalogue |
| Profile catalogue | Separate master catalogue |
| Investigation catalogue | Separate master catalogue |
| Response scales | Seven-point scales plus non-numeric options |
| Context and impact | Separate from frequency |
| Evidence aggregation | Characteristic level |
| Uncertainty | Explicitly represented |
| Question budget | Configurable |
| Stopping conditions | Required |
| Reactivation | Supported |
| Profile results | Educational associations only |
| Diagnostic probabilities | Not allowed |
| Versioning | Required |
| Historical results | Must preserve interpretation and question versions |

---
## 25. Open decisions

The following should be resolved during implementation planning:

   1. JSON files versus database persistence.
   2. Whether users can save sessions without accounts.
   3. Whether sessions can resume across devices.
   4. Whether the first version uses only deterministic routing.
   5. Whether users can choose exploration depth.
   6. Whether all eight domains are included in the first release.
   7. Which profiles have sufficient verified evidence for inclusion.
   8. Whether the first release supports one language or multiple languages.
   9. How scientific content is reviewed and approved.
   10. How user data is retained and deleted.

---
## 26. Product positioning

This product should feel like a guided investigation into personal
experiences.

It should not feel like an online diagnostic test.

The user is not being assigned a label. They are discovering patterns in
how they:

   - Focus and regulate attention.
   - Organize and execute tasks.
   - Process sensory information.
   - Communicate and interact.
   - Think and solve problems.
   - Experience and regulate emotions.
   - Learn and pursue interests.
   - Adapt to environments and expectations.

Scientific literature informs the questions and educational suggestions. It
does not automatically validate the questionnaire as a clinical instrument.

*Central product principle: Help people understand their experiences and
discover useful concepts to explore, without pretending to determine who
they are.*