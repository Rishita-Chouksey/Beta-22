# PRD: Scheme Eligibility Guide (Hackathon)

Oct 31, 2026 · @Shreya

## 1. Problem and goal

Citizens miss schemes they qualify for because the rules are scattered, written in dense language, and a wrong answer costs them either way. We build a guest-first web tool that tells one citizen which schemes they may qualify for, why, and which documents to arrange, in Hindi or English, by text or voice.

**What a win looks like at the demo:** a judge picks one of three personas, answers a few questions (or types one sentence about themselves), and sees three lists: Eligible, Not sure, Not eligible. Every scheme shows the rule that decided it, the official link, the date the rules were last checked, and a printable document checklist. A messy or incomplete input produces "Not sure" with what would change the answer, never a guess.

## 2. Personas

We design for three specific people, not "all citizens". Candidate schemes below are our starting list; every rule must be read from the official source before it goes into a rules file.

|  | Rural farmer | Widowed woman | College-going girl |
| --- | --- | --- | --- |
| Situation | Small landholding, Hindi-first, phone is shared or basic | Lost husband, may have children, little paperwork in her own name | First-generation student, comfortable on phone, unsure which scholarships fit |
| Main tension | Land and bank documents decide everything; does not know her or his exact income | Does not know what she is entitled to; rules differ between centre and state | Too many scholarships; one-scholarship-only rules; deadlines |
| Needs from the tool | Short questions in Hindi, voice, no income figure demanded | Plain-language result, a short document list, where to get a death certificate | Scholarship list in one place, clash warnings, document checklist |
| Candidate schemes (to verify) | PM-KISAN, PM Fasal Bima Yojana, Kisan Credit Card, Ayushman Bharat PM-JAY | Indira Gandhi National Widow Pension (NSAP), Ujjwala, Ayushman Bharat PM-JAY, one state widow pension | Central Sector Scholarship for college students, AICTE Pragati (if technical), one state scholarship, Post Matric scholarship |

**Scheme coverage:** there is no cap on schemes, only on personas (three). The list above is a starting shortlist. A scheme with a verified rules file can be shown as Eligible, Not eligible or Not sure. Any other scheme we know of is shown as Not sure with the label "no current rules in this tool" and its official link, because the tool must never say Eligible when guessing. Adding a scheme later is one new rules file. We write rules for as many schemes as time allows, and at least 5 must be fully tested.

**Before building:** each teammate talks to one real person who fits a persona for 10 minutes and writes down one thing that surprised them. This is evidence for the "understanding the user" criterion.

## 3. Existing solutions and the gap

Discovery and document storage already exist; what is missing is an honest, explained, document-ready answer for one person in their own language. The gaps below are our hypotheses and must be checked by using each product before the pitch.

| Existing option | What it does | Gap we think we fill (verify) |
| --- | --- | --- |
| [MyScheme](https://www.myscheme.gov.in/) | Government discovery portal: enter details, get matching schemes, then apply ([PIB note](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2022/sep/doc2022921106701.pdf)) | Result is a list of matches; check whether it shows the deciding rule, uncertainty near limits, or a per-person document checklist |
| UMANG and state portals | Many services in one app, or one portal per state | Citizen still has to know what to look for; steps differ by portal |
| DigiLocker | Stores and shares government documents | Stores documents, does not tell which ones a given scheme needs |
| Cyber cafe or local agent | Human help filling forms | Costs money, depends on the agent being right, no explanation |
| Open-source projects pairing an LLM with scheme data (example: [Right](https://github.com/Niss54/Right)) | Chat-style scheme finder with voice | LLM judging eligibility can guess; judges may have seen similar demos |

**Our difference in one line:** eligibility is decided by plain, checkable rules, not by a language model, so the tool can say exactly which rule decided and when it does not know.

## 4. Scope

Judges reward a stable core flow over a wide one, so the build list is short and the "not built" list is written down with reasons.

**We build**

- Guest-first flow: no login needed to get a result
- Two ways to describe yourself: short questionnaire, or free text that is parsed and then confirmed by the citizen
- Three result lists: Eligible, Not sure, Not eligible (with filters)
- Scheme page: summary, key rules highlighted, document checklist with sample image and where to get each document, application steps, official link
- Printable or downloadable checklist
- Photo of a form, read in memory to explain confusing fields, deleted when the session ends
- Chatbot guide on every screen, Hindi and English, voice in and voice out
- One extra: a third language
- Rules stored one file per scheme, with source link and last-checked date

**We deliberately do not build**

| Left out | Why |
| --- | --- |
| Login, passwords, saved profiles | Not needed for the core flow and it adds stored personal data; planned for later |
| Document locker (upload once, keep) | Same reason; also needs secure storage we cannot prove in 24 hours |
| Auto-submitting applications | Wrong data submitted for a citizen is worse than a link to the official site |
| Live scraping of MyScheme | Its terms prohibit bots and scrapers without written permission (see section 9) |
| LLM deciding eligibility | It can guess; the PS forbids saying "eligible" when guessing |
| Many states | State rules multiply the work; state schemes cover Maharashtra only, and central schemes cover everyone |
| Auto-editing rules from the web | A changed rule must be checked by a person; auto-update only flags stale or changed rules |

## 5. Functional requirements

P0 means the demo fails without it; P1 means build if P0 is stable.

| ID | Requirement | Covers PS item | Priority |
| --- | --- | --- | --- |
| F1 | Hindi and English on every screen, question and result, with one visible switch | Bilingual interface | P0 |
| F2 | Answer by voice and hear questions and results read aloud, in both languages | Voice support | P0 |
| F3 | Ask only questions that can change a result, in an order driven by the rules (most deciding first) | Fewest questions | P0 |
| F4 | Free text is parsed into fields, shown back to the citizen, and used only after confirmation | Fewest questions, never guess | P0 |
| F5 | Each scheme result names the deciding rule in simple words | Explain the decision | P0 |
| F6 | Missing or borderline answers give "Not sure" with what would change it; missing or stale rules are stated | Say what it is not sure about | P0 |
| F7 | Every scheme shows official link, last-checked date, and a warning if the rules are older than the allowed age | Source information | P0 |
| F8 | Printable or downloadable document checklist per scheme, with sample image and where to get each document (online link, or offline office only where needed) | Document checklist | P0 |
| F9 | Change one scheme by editing one rules file; nothing else changes | Easy to update | P0 |
| F10 | Nothing stored beyond the session; one "clear everything" button | Privacy | P0 |
| F11 | Not Eligible list with filters, each with the rule that failed | Explain the decision | P1 |
| F12 | Clash warnings between schemes (for example, one scholarship only) | Answers that disagree | P1 |
| F13 | Form photo explained field by field, image deleted at session end | Own idea, problem 4 | P1 |
| F14 | Third language | Extra points | P1 |
| F15 | Scheduled check that flags rules past their review date | Easy to update | P1 |

## 6. Eligibility honesty model

The tool says "Eligible" only when every rule passes on an answer the citizen confirmed. Each rule returns pass, fail or unknown, and the scheme result follows mechanically.

| Scheme result | When it happens | Tab shown in |
| --- | --- | --- |
| Eligible | Every rule passes on confirmed answers, none within the borderline margin | Eligible |
| Not eligible | At least one rule fails clearly; the failed rule is shown | Not eligible |
| Not sure | No rule fails, but at least one is unknown or the value is within the margin of a limit | Not sure |
| No current rules | The scheme has no rules file, or its last-checked date is past the allowed age | Not sure, with a distinct label |

**Rules for uncertainty**

1. **Unknown number (for example income):** offer ranges such as "below 1 lakh" or "1 to 2.5 lakh"; if the range straddles the limit, the result is Not sure and says which exact figure would settle it.
2. **Borderline:** a value within a set margin of a limit (start with 10 percent) is Not sure, with the limit and the margin stated.
3. **Free text:** extracted values are shown as "Here is what I understood" and are unknown until the citizen confirms them.
4. **Stale rules:** each scheme has a maximum age (start with 90 days). Past it, the result carries a visible "rules may be out of date" label.
5. **Disagreement or unverifiable rule:** when a rule depends on something the tool cannot check (for example a land record), the result says so and points to the official office or helpline, not a guess.

**Where the language model is allowed:** extracting fields from free text, rewording rule text in simple Hindi and English, the chatbot, and explaining form fields. **Where it is not allowed:** deciding eligibility, setting limits, or writing the checklist from memory.

**Open point:** your idea that "all documents available means eligible" mixes two things. Documents show a citizen can apply; they do not prove a rule is met. We suggest the follow-up questionnaire settles Not sure, and the checklist shows application readiness separately.

## 7. Privacy decisions

The default is to keep nothing: no account, no server-side profile, no stored income. This is also what protects someone using a relative's or a shop's phone.

| Data | Where it lives | How long | Why |
| --- | --- | --- | --- |
| Answers (age, income range, land, category) | Browser tab memory only | Until the tab closes, or 10 minutes idle, or "Clear everything" | Needed only to compute the result |
| Name, phone, email | Not collected | Not applicable | No login in the core flow, so nothing to leak |
| Form photo | Sent for reading, then dropped | Deleted when the session ends | Only to explain fields; never saved |
| Data sent to the language model | Confirmed profile fields only, no name, phone or documents | Not kept by us | The model never sees documents or identity |
| Server logs | Event names and error codes | Short-lived | No profile values, so logs cannot expose a citizen |
| Downloaded checklist | Citizen's device | Citizen's choice | Lists schemes and documents, no income or personal answers |

**Shared-phone rules**

- Use session memory only; no persistent browser storage, no answers in the web address, no autofill on forms
- A visible "Clear and exit" button, and a reminder to use it on someone else's phone
- **How we check:** after a demo session, open the browser's storage and history on that device and confirm no profile values remain

**Plain-language explanation for the judges:** we do not store what we do not need; the less we hold, the less can be lost, and the citizen decides what leaves their phone.

## 8. Extra feature: third language

**Who it is for:** a citizen who is not comfortable in Hindi or English, most likely in the home state whose schemes we cover. Our home state is Maharashtra, so the third language is Marathi.

**Default suggestion:** Marathi, because it is the main language of our home state. We test early that speech-to-text and text-to-speech work well for Marathi; if they do not, the app shows Marathi text with typed answers only.

**How we build it cheaply:** every screen string, question and rule explanation lives in a language file, so a new language is a new file plus a glossary, with no code change. This also shows the "easy to update" idea.

**How we know the translations of official terms are right**

- A glossary of official scheme and document names, copied from the scheme's own official page in that language, never machine-translated
- Official English term shown in brackets next to the translated one
- One native speaker outside the team reads the ten most important screens; their corrections go back into the glossary
- Anything not in the glossary falls back to the English official term, and is not translated by the model

## 9. Data source: MyScheme API and fallback

We cannot rely on a live MyScheme feed inside 24 hours, so the app's decisions come from our own rules files and MyScheme is a reference, not a dependency.

**What we found (searched today, not yet tested by us)**

- [API Setu](https://docs.apisetu.gov.in/document-central/explore-apisetu/Overview.html) is the government API marketplace, and access to an API is granted only after the publisher approves the subscription. We found no public, documented MyScheme eligibility API there.
- Community projects call the same JSON endpoint the MyScheme website uses, with a key (example: [this MCP server](https://glama.ai/mcp/servers/jzk90j5pzh)). That endpoint is unofficial and may change or block us.
- The [MyScheme terms of use](https://www.myscheme.gov.in/hi/terms-of-use) say automated access such as bots or scrapers is prohibited unless authorised in writing, and that the content is not a statement of law.
- MyScheme's descriptive text is not a machine-readable rule set. Even with access, a person must turn it into rules.

**Fallback ladder**

1. **Today:** write to the MyScheme team at the address on the [API Setu contact page](https://apisetu.gov.in/contact) asking for API access. Treat any reply as a bonus.
2. **Core plan:** hand-written rules files, one per scheme, each with the official source link and the date a teammate last read it.
3. **Faster drafting:** paste an official scheme page into the model to propose a draft rules file; a teammate checks it against the page before it is saved.
4. **If we get access:** use the API only to detect that a scheme's text changed and raise a review flag, never to edit rules automatically.

**What we tell the judges:** the data is verified, dated and easy to update; it is not scraped, and not guessed by a model.

## 10. Success metrics and how we know it works

For the hackathon, "works" means the rule engine is provably right on a fixed test set and the flow is usable by someone who has never seen it.

| Check | Target | How we measure |
| --- | --- | --- |
| Rule engine accuracy | 100 percent match on a hand-checked test set of about 20 profiles | Run test profiles through the engine, compare with answers a teammate worked out from the official page |
| No false "Eligible" | 0 cases where a required answer is missing but the result says Eligible | Automated test: blank each required field in turn |
| Borderline handling | Every profile within the margin of a limit lands in Not sure | Test profiles at the limit, just below and just above |
| Questions asked | 8 or fewer per persona | Count questions in a full run for each persona |
| Time to result | Under 3 minutes for a first-time user | One person outside the team tries it while we watch, without help |
| Voice | Hindi voice answer is understood in a quiet room for the core questions | Test with two speakers; fall back to typing if it fails |
| Privacy | No profile values left in browser storage or history after a session | Inspect storage after a demo run |
| Update test | Change one scheme's limit and see the result change with no other edit | Do it live in the demo |

**After the hackathon (how we would know it helped):** share of citizens who go from "may qualify" to starting an application, and share who reach the right document on the first try.

## 11. Risks and open questions

**Risks**

| Risk | What we do |
| --- | --- |
| Scheme rules are read wrongly | Each rules file is checked by a second teammate against the official page before it is marked verified |
| Free-text parsing misreads a field | Confirm step before any decision; unconfirmed fields count as unknown |
| Voice recognition is poor in a noisy hall | Typing always works; voice is tested early, not last |
| Time runs out | P0 list in section 5 is the cut line; Not Eligible filters and form photo are P1 |
| A judge gives an unseen profile | Engine returns Not sure with the missing field named, never an error or a guess |
| Source link or rules go stale or break during demo | Stale label shows; the app still works from local rules files |
