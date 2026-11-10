# Example outputs

Generated 09 November 2026 by `scripts/generate_examples.py` using `claude-sonnet-5-5` (routing, answers, summaries) and `claude-haiku-5-5` (per-document extraction).

## Executive summary

**Request:** Summarise the documents for a senior audience

**Routed to:** `executive_summary` (User wants a summary of the documents for senior stakeholders.) · routed by model · 31.9s

**Bottom line:** The UK has a clear AI direction, but foundation model markets depend on a few firms' control of compute and data, so government must keep markets open while building trusted adoption.

## Key messages
- The CMA finds competition currently vibrant, but a few large firms control compute, data and chips. Public training data may run out within about three years.
- The AI Opportunities Action Plan (13 January 2025) makes 50 recommendations, including 20x more AI research compute by 2030 and a UK Sovereign AI unit.
- The AI Playbook (10 February 2025) gives civil servants 10 principles. Government AI must also meet Secure by Design principles.
- Consumer law already covers AI-generated content. The DMCC Bill will expand CMA powers.

## Main risks
- **Barriers to entry:** Frontier model compute reportedly cost over $100 million for GPT-4, and none of the three biggest cloud providers offers NVIDIA A100 chips in the UK.
- **Lock-in and foreclosure:** Vertically integrated firms could restrict rivals' access or tie services. The CMA says it is too early to judge data feedback effects.
- **Consumer harm and accountability:** Hallucinations are unlikely to be eliminated, fake reviews, phishing and hidden advertising may increase, and responsibility is hard to pinpoint.

## Opportunities
- Scan, Pilot, Scale could speed adoption.
- Sovereign AI capability and more compute could reduce reliance on a few suppliers.
- Principles on disclosure, portability, interoperability and benchmarks could build trust and keep markets open.

## Recommended next steps
- Seek costings and long-term funding for the Action Plan, which lacks costed detail.
- Review the Playbook and government response in full; the summaries seen cannot confirm owners or timelines.
- Engage the CMA and Government AI Security Team early, and require supplier agreements before sharing sensitive data with third-party AI providers.

*285 words · based on 11 documents*

<details><summary>Sources</summary>

- AI Foundation Models Initial Report
- AI Foundation Models Short Report
- AI Opportunities Action Plan
- AI Opportunities Action Plan Publication
- AI Playbook for UK Government
- AI Safety Institute
- AI Security Guidance
- Foundation Model Taskforce
- GDS AI Index
- Generative AI Policy
- Guide to Using AI in Public Sector

</details>

---

## Risk extraction

**Request:** What are the key risks?

**Routed to:** `extract_insights` (User asks for the key risks across the documents.) · routed by model · 20.0s

### Risks

| # | Item | Detail | Owner | Date | Priority | Source |
|---|---|---|---|---|---|---|
| 1 | **Compute and chip concentration raises barriers to entry** | NVIDIA leads AI accelerators and Google offers TPUs only on GCP. Frontier training costs run to about $100 million, and ever-larger models may confine development to firms with existing infrastructure, concentrating the market. | NVIDIA; Google; Microsoft; OpenAI; Smaller FM entrants; Smaller FM developers | - | High | AI Foundation Models Initial Report, p.34; AI Foundation Models Initial Report, p.44; AI Foundation Models Short Report, p.12 |
| 2 | **Compute access favours CSP partners; UK regions lag** | Priority access and cheaper rates go to few CSP partners, so startups may struggle. No major CSP offers NVIDIA A100s in the UK, and TPUv4 clusters are US-only, which hampers UK developers using sensitive data. | Smaller FM developers and startups; UK developers; AWS, Microsoft Azure, GCP | - | High | AI Foundation Models Initial Report, p.36; AI Foundation Models Initial Report, p.37 |
| 3 | **Proprietary data may become a competitive necessity** | High-quality public language data may be exhausted within three years. Proprietary data could then become a key competitive factor, leaving developers dependent on a few firms and prompting CMA concern if rivals' access is unduly restricted. | FM developers; data providers; firms with leading positions in other markets | within the next three years | High | AI Foundation Models Initial Report, p.29; AI Foundation Models Initial Report, p.43; AI Foundation Models Short Report, p.27 |
| 4 | **Vertical integration may foreclose rivals and tip markets** | Hyperscalers own data centres and data repositories. Integrated firms may withhold inputs or impose restrictive terms, and real-time data feedback from downstream services could create first-mover advantages that concentrate markets. | Microsoft; Amazon; Google; Vertically integrated firms; CSPs such as Microsoft, Amazon and Google; Integrated FM developers and downstream deployers | - | High | AI Foundation Models Initial Report, p.17; AI Foundation Models Short Report, p.25; AI Foundation Models Short Report, p.27 |
| 5 | **Customer and vendor lock-in** | Accumulated customisation may stop businesses and consumers switching without starting afresh, weakening competition unless data is portable and services interoperable. The public compute ecosystem should use varied hardware providers to avoid vendor lock-in. | Consumers and businesses; integrated ecosystem providers; Government | - | High | AI Foundation Models Short Report, p.23; AI Opportunities Action Plan |
| 6 | **Hallucinations and unclear accountability harm consumers** | FMs produce convincing but incorrect outputs that are unlikely to be eradicated. In complex supply chains, responsibility for failures is hard to identify, weakening incentives to reduce harm and complicating redress. | FM developers; businesses deploying FMs; deployers in supply chains | - | High | AI Foundation Models Short Report, p.29; AI Foundation Models Short Report, p.30; Guide to Using AI in Public Sector, p.20 |
| 7 | **Biased or poor-quality data drives discriminatory outputs** | Error-strewn or unrepresentative training data, including legacy government datasets, can produce poor results and bias against groups, including those with protected characteristics. Continuous governance checks and human-in-the-loop review are needed. | - | - | High | Guide to Using AI in Public Sector, p.25; Guide to Using AI in Public Sector, p.38; Generative AI Policy |
| 8 | **Data protection, misleading content and deepfake exposure** | Sensitive data must not go to third-party AI providers without agreements. Generative AI must not mislead or alter content meaning, AI avatars risk deepfakes, and automated decisions need GDPR/DPA 2018 safeguards. | Government communicators; Government Communications | - | High | Generative AI Policy; Guide to Using AI in Public Sector, p.13 |
| 9 | **Mergers, regulation and trust may constrain competition and adoption** | Mergers could substantially lessen FM competition. Ineffective regulation may hold back adoption, and adoption depends on public and business trust. Ministers agreed regulation must keep people safe without preventing innovation. | Regulators; government; Public and business; Cabinet Ministers | - | High | AI Foundation Models Short Report, p.37; AI Opportunities Action Plan; Foundation Model Taskforce |
| 10 | **Security and sovereignty risks of AI infrastructure** | AI infrastructure carries sustainability and security risks, requiring secure private compute and UK Intelligence Community collaboration. Generative AI security risks and national security exposure also require safe deployment. | Government; UK Intelligence Community; Generative AI security community; Marc Warner, CEO of Faculty (commentary) | - | Medium | AI Opportunities Action Plan; AI Security Guidance; Foundation Model Taskforce |

<details><summary>Sources</summary>

- AI Foundation Models Initial Report, p.17
- AI Foundation Models Initial Report, p.29
- AI Foundation Models Initial Report, p.34
- AI Foundation Models Initial Report, p.36
- AI Foundation Models Initial Report, p.37
- AI Foundation Models Initial Report, p.43
- AI Foundation Models Initial Report, p.44
- AI Foundation Models Short Report, p.12
- AI Foundation Models Short Report, p.23
- AI Foundation Models Short Report, p.25
- AI Foundation Models Short Report, p.27
- AI Foundation Models Short Report, p.29
- AI Foundation Models Short Report, p.30
- AI Foundation Models Short Report, p.37
- AI Opportunities Action Plan
- AI Security Guidance
- Foundation Model Taskforce
- Generative AI Policy
- Guide to Using AI in Public Sector, p.13
- Guide to Using AI in Public Sector, p.20
- Guide to Using AI in Public Sector, p.25
- Guide to Using AI in Public Sector, p.38

</details>

---

## Action extraction

**Request:** List the actions and who owns them

**Routed to:** `extract_insights` (User wants actions and their owners across the documents.) · routed by model · 21.0s

### Actions and owners

| # | Item | Detail | Owner | Date | Priority | Source |
|---|---|---|---|---|---|---|
| 1 | **Ensure fair access to key FM inputs and curb leveraging of market power** | Developers need access to data, computing power, capital and expertise on fair commercial terms. Firms should not use leading positions in other markets to unduly restrict competitors or other FM developers. | Regulators; FM developers; incumbent firms | - | High | AI Foundation Models Initial Report, p.53; AI Foundation Models Short Report, p.18 |
| 2 | **Keep FM markets open, interoperable and competition-law compliant** | Choice of deployment options, interoperability, data portability and a mix of open and closed-source models support good outcomes. Avoid self-preferencing, tying and bundling; check cooperation and mergers against competition law. | Regulators and FM market participants | - | High | AI Foundation Models Initial Report, p.78; AI Foundation Models Initial Report, p.105; AI Foundation Models Short Report, p.16 |
| 3 | **Clearly disclose AI-generated content to consumers** | Consumers should be told when content is FM-generated, along with its risks and limitations. Disclosure alone may not suffice, and watermarking practicality is unclear, so it should complement technical approaches. | FM developers and deployers | - | High | AI Foundation Models Initial Report, p.89; AI Foundation Models Initial Report, p.98; AI Foundation Models Short Report, p.35 |
| 4 | **Address hallucinations and provide accurate information** | Firms should do all they can to address inherently false outputs and prevent consumer harm. Developers should give business and consumer customers sufficient, understandable and accurate information to make informed choices. | Firms developing and deploying FMs | - | High | AI Foundation Models Initial Report, p.97; AI Foundation Models Short Report, p.32 |
| 5 | **Review consumer and competition law obligations across the FM supply chain** | Businesses developing FMs or incorporating them into consumer products should consider carefully whether they meet consumer law and keep this under review as practice and law develop. | Businesses developing FMs and downstream supply chain | - | High | AI Foundation Models Initial Report, p.106; AI Foundation Models Short Report, p.33; AI Foundation Models Short Report, p.36 |
| 6 | **Create UK Sovereign AI unit to maximise UK stake in frontier AI** | A new unit empowered to partner with the private sector should make concentrated bets, invest directly, form joint ventures and spin out AI companies to build national champions. | UK Sovereign AI (new unit) | - | High | AI Opportunities Action Plan |
| 7 | **Establish AI Growth Zones with streamlined planning** | Growth Zones should accelerate data centre build-out, with at least one nominated quickly. Culham Science Centre is suggested as a pilot site. | Government | Quickly | High | AI Opportunities Action Plan |
| 8 | **Reform UK text and data mining regime** | The regime should be reformed to be at least as competitive as the EU, since IP uncertainty is described as hindering innovation and needing urgent resolution. | Government | Urgently; no date given | High | AI Opportunities Action Plan |
| 9 | **Maintain human oversight, consent and supplier adherence for government generative AI** | No public-facing generative AI output without human oversight. Written consent is required before replicating a human likeness, and all contracted and framework suppliers must adhere to the policy. | Government communicators and technical teams | - | High | Generative AI Policy |
| 10 | **Establish a governance framework for public sector AI** | Governance should cover explainability, fairness, legal compliance, achievement of purpose, a clear owner, monitoring cadence, public narrative fit and code validation. | - | - | High | Guide to Using AI in Public Sector, p.34 |

<details><summary>Sources</summary>

- AI Foundation Models Initial Report, p.105
- AI Foundation Models Initial Report, p.106
- AI Foundation Models Initial Report, p.53
- AI Foundation Models Initial Report, p.78
- AI Foundation Models Initial Report, p.89
- AI Foundation Models Initial Report, p.97
- AI Foundation Models Initial Report, p.98
- AI Foundation Models Short Report, p.16
- AI Foundation Models Short Report, p.18
- AI Foundation Models Short Report, p.32
- AI Foundation Models Short Report, p.33
- AI Foundation Models Short Report, p.35
- AI Foundation Models Short Report, p.36
- AI Opportunities Action Plan
- Generative AI Policy
- Guide to Using AI in Public Sector, p.34

</details>

---

## Deadlines

**Request:** What deadlines or milestones are mentioned?

**Routed to:** `extract_insights` (User asks for deadlines and milestones mentioned across the documents.) · routed by model · 12.2s

### Deadlines and milestones

| # | Item | Detail | Owner | Date | Priority | Source |
|---|---|---|---|---|---|---|
| 1 | **DMCC Bill to expand CMA enforcement powers** | The CMA expects the Digital Markets, Competition and Consumers Bill to come into force in the near future. It would give the CMA powers to decide consumer law breaches, impose fines and order compensation, plus a digital markets regime. | CMA | Anticipated in the near future | High | AI Foundation Models Initial Report, p.107 |
| 2 | **CMA to publish update on guiding principles** | The CMA will publish an update on its thinking on the principles and how they have been received and adopted, also reflecting on further market developments. | CMA | Early 2024 | High | AI Foundation Models Short Report, p.38; AI Foundation Models Initial Report, p.122 |
| 3 | **Long-term AI infrastructure plan with 10-year investment commitment** | Government should set out within six months a long-term plan for UK AI infrastructure needs, backed by a 10-year investment commitment. | Government | Within 6 months | High | AI Opportunities Action Plan |
| 4 | **Expand AI Research Resource by at least 20x by 2030** | The AIRR should be expanded at least 20x by 2030, starting within six months. This need not mean a 20x rise in investment if procurement is smart. | Government | Starting within 6 months; by 2030 | High | AI Opportunities Action Plan |
| 5 | **Training tens of thousands of AI professionals by 2030** | A short-term target to train tens of thousands of AI professionals by 2030 is proposed to bridge the estimated supply-demand gap, to be reached over the next five years. | Government | By 2030; over the next 5 years | High | AI Opportunities Action Plan |
| 6 | **First public-service pilots expected within six months** | The first pilots targeting public services are expected to launch in the next six months. | Foundation Model Taskforce | In the next six months | High | Foundation Model Taskforce |
| 7 | **Ofcom cloud infrastructure market study final report** | Ofcom intends to publish its final report on the UK cloud infrastructure market study, relevant to compute access for FM development. It may trigger a referral to the CMA for independent investigation. | Ofcom | no later than 5 October 2023 | Medium | AI Foundation Models Initial Report, p.14; AI Foundation Models Initial Report, p.108; AI Foundation Models Short Report, p.13 |
| 8 | **EU AI Act expected final form** | The EU AI Act is aimed to be in final form by the end of 2023, though when it would come into force is unclear and it remains subject to amendment. | European Union | End of 2023 | Medium | AI Foundation Models Initial Report, p.114 |
| 9 | **Quick-win adoption ideas from Digital Centre of Government** | In the next three months, the Digital Centre of Government should identify quick wins supporting the Scan, Pilot, Scale approach and public-private reinforcement. | Digital Centre of Government | In the next 3 months | Medium | AI Opportunities Action Plan |
| 10 | **Headhunting capability and talent measures within the next year** | Government should establish an internal headhunting capability to attract elite individuals to the UK, with actions framed as within the next year. | Government | Within the next year | Medium | AI Opportunities Action Plan |

<details><summary>Sources</summary>

- AI Foundation Models Initial Report, p.107
- AI Foundation Models Initial Report, p.108
- AI Foundation Models Initial Report, p.114
- AI Foundation Models Initial Report, p.122
- AI Foundation Models Initial Report, p.14
- AI Foundation Models Short Report, p.13
- AI Foundation Models Short Report, p.38
- AI Opportunities Action Plan
- Foundation Model Taskforce

</details>

---

## Stakeholders

**Request:** Who are the main stakeholders?

**Routed to:** `extract_insights` (User asks for the main stakeholders across the documents.) · routed by model · 11.0s

### Stakeholders

| # | Item | Detail | Owner | Date | Priority | Source |
|---|---|---|---|---|---|---|
| 1 | **CMA as lead competition and consumer authority reviewing AI foundation models** | The CMA, an independent non-ministerial department, is the UK's principal competition and consumer protection authority. It is conducting this review in response to government expectations on AI innovation. | CMA | - | High | AI Foundation Models Initial Report, p.5 |
| 2 | **Major cloud providers control compute and FM distribution while competing downstream** | AWS, Microsoft Azure and Google Cloud are the main CSPs with acceleration capabilities. They partner with FM developers, host FMs for inference and compete with customers downstream; Microsoft has an exclusive OpenAI cloud partnership. | AWS; Microsoft Azure; Google Cloud Platform | - | High | AI Foundation Models Initial Report, p.36; AI Foundation Models Initial Report, p.67 |
| 3 | **Ofcom cloud study may lead to CMA market investigation** | Ofcom intends to publish its final report by 5 October 2023 and has proposed referring public cloud infrastructure services to the CMA, which would examine adverse competition effects, including FM-related issues. | Ofcom; CMA | no later than 5 October 2023 | High | AI Foundation Models Short Report, p.13 |
| 4 | **Government-industry Foundation Model Taskforce with direct ministerial reporting** | The taskforce brings together government and industry experts and reports directly to the Prime Minister and Technology Secretary. It advances UK sovereign FM capability, with £100 million initial funding; Matt Clifford advises on its development during the Chair appointment. | Prime Minister and Technology Secretary | - | High | Foundation Model Taskforce; AI Foundation Models Initial Report, p.6 |
| 5 | **AI Security Institute and government AI security bodies** | The DSIT-based AI Safety Institute is now the AI Security Institute, aiming to minimise surprise from rapid AI advances. The Government AI Security Team, within the Government Cyber Unit, advises on AI security risks. | Department for Science, Innovation and Technology | - | High | AI Safety Institute; AI Security Guidance |
| 6 | **AI Opportunities Action Plan: DSIT publication led by Matt Clifford** | DSIT published the independent Action Plan as a roadmap for government. It is led by Matt Clifford CBE, Chair of ARIA, and proposes AI Sector Champions and SME-focused adoption support. | Department for Science, Innovation and Technology; Matt Clifford CBE; Advanced Research and Invention Agency (ARIA) | 13 January 2025 | High | AI Opportunities Action Plan Publication; AI Opportunities Action Plan |
| 7 | **Government Digital Service publishes AI Playbook and Responsible AI Advisory Panel** | GDS published the AI Playbook for civil servants and government organisations. Its Responsible AI Advisory Panel has issued insights on responsible government AI use, though full content is not given. | Government Digital Service | 10 February 2025 | High | AI Playbook for UK Government; GDS AI Index |
| 8 | **International AI Safety Report to inform AI Action Summit** | The First International AI Safety Report is intended to inform discussions at the AI Action Summit. | - | 29 January 2025 | Medium | AI Safety Institute |
| 9 | **Digital Markets Unit and DRCF shape forthcoming regulatory regime** | The Digital Markets, Competition and Consumers Bill will give the CMA powers for a pro-competition digital markets regime via the DMU. The CMA will work with other regulators, including through the DRCF, on FM regulation. | CMA Digital Markets Unit; Digital Regulation Cooperation Forum | - | Medium | AI Foundation Models Initial Report, p.6; AI Foundation Models Short Report, p.36 |
| 10 | **FM developers and wider stakeholders targeted for engagement and voluntary commitments** | The CMA plans to consult consumer groups, developers (Google, Meta, OpenAI, Microsoft, NVIDIA, Anthropic), deployers, academics and regulators. Developers launched the Frontier Model Forum and made voluntary White House commitments. | Consumer groups; leading FM developers; major deployers; academics; government; fellow regulators | July 2023 | Medium | AI Foundation Models Short Report, p.38; AI Foundation Models Initial Report, p.117 |

<details><summary>Sources</summary>

- AI Foundation Models Initial Report, p.117
- AI Foundation Models Initial Report, p.36
- AI Foundation Models Initial Report, p.5
- AI Foundation Models Initial Report, p.6
- AI Foundation Models Initial Report, p.67
- AI Foundation Models Short Report, p.13
- AI Foundation Models Short Report, p.36
- AI Foundation Models Short Report, p.38
- AI Opportunities Action Plan
- AI Opportunities Action Plan Publication
- AI Playbook for UK Government
- AI Safety Institute
- AI Security Guidance
- Foundation Model Taskforce
- GDS AI Index

</details>

---

## Factual question

**Request:** What is the AI Safety Institute's mission?

**Routed to:** `answer_question` (Specific factual question about the AI Safety Institute's mission, best answered by searching the documents.) · routed by model · 4.0s

The AI Safety Institute's mission is "to minimise surprise to the UK and humanity from rapid and unexpected advances in AI" [S1].

Note that the same page says the AI Safety Institute is now called the AI Security Institute [S1]. It sits within the Department for Science, Innovation and Technology [S1].

The excerpts do not give a fuller statement of the mission beyond that sentence. For wider context, the AI Opportunities Action Plan describes the Institute's work on model evaluations, foundational safety and societal resilience research. It also notes that the Institute was the first safety institute to conduct pre-deployment evaluations of frontier models [S2].

<details><summary>Sources</summary>

- [S1] AI Safety Institute
- [S2] AI Opportunities Action Plan

</details>

---

## Factual question

**Request:** What concerns does the CMA raise about competition in foundation models?

**Routed to:** `answer_question` (Specific factual question about CMA's competition concerns in the loaded documents.) · routed by model · 10.2s

The excerpts don't name the CMA as the author; they use "we". Subject to that, the reports raise these competition concerns:

- **Concentration risk:** Past technology markets show network effects and switching barriers can lead to consolidation, weak competition and "winner-takes-most" outcomes. The report tests whether this applies to FMs, looking at data, compute, expertise, funding and open-source models as entry barriers [S3].
- **Vertical integration and partnerships:** These can bring benefits but can also distort competition. One example is a vertically integrated firm with market power imposing restrictive partnership terms that stop a partner competing downstream [S2].
- **Structural features:** Economies of scope could raise barriers for new entrants. Switching costs could arise, especially "artificial" ones created by product design to weaken competition [S7]. The authors have not yet reached a view on how likely these are [S7].
- **Lock-in:** Closed ecosystems are a risk unless consumers can port their data easily [S2].
- **Concerning outcome:** Firms have limited FM options and struggle to switch, data feedback effects harm competition, and consumers cannot make informed choices [S4][S6].
- **Uncertainty:** FM services are at a very early stage, so it is hard to say whether competition will increase or concerns will arise [S4]. FMs could also exacerbate existing concerns or create new ones [S4].

<details><summary>Sources</summary>

- [S2] AI Foundation Models Short Report, p.24
- [S3] AI Foundation Models Initial Report, p.28
- [S4] AI Foundation Models Initial Report, p.71
- [S6] AI Foundation Models Initial Report, p.71
- [S7] AI Foundation Models Initial Report, p.69

</details>

---

## Factual question

**Request:** What does the GCS policy say about using generative AI to create images?

**Routed to:** `answer_question` (Specific factual question about a policy's content on AI image generation.) · routed by model · 8.6s

The policy lists image generation as a permitted use, subject to general safeguards. The excerpts do not contain image-specific rules beyond those below.

**Permitted uses**
- Generating variations of campaign imagery optimised for different platforms and formats [S6].
- Producing region-specific visual content that resonates with local communities [S6].
- Creating infographics that make complex government statistics more accessible [S6].
- Adapting existing visual content, for example resizing the aspect ratio to fit different formats or screens [S6].

**Safeguards that apply**
- **Factuality:** content must not mislead, and existing digital content must not be altered in a way that removes or replaces its original meaning [S2].
- **Consent:** written consent from a human is required before their likeness is replicated using AI. A record will be made available via an official channel, including in the content's description and alt text [S6]. The aim is to distinguish legitimate communications from deep-fakes [S3].
- **Human oversight:** generative AI must not be used to deliver communications without human oversight. For static content, this involves the creator(s) and the lead responsible for the communications activity [S3].
- **Declaring use:** other uses of generative AI will be declared where doing so supports a campaign's key messages [S3].
- **Values:** generative AI will not be applied where it conflicts with the Civil Service Code or the Government Publicity Conventions [S3].

**Gap:** the August 2025 update reportedly added detail on where AI-generated content should be labelled [S7], but the excerpts do not give the specific labelling rules for images.

<details><summary>Sources</summary>

- [S2] Generative AI Policy
- [S3] Generative AI Policy
- [S6] Generative AI Policy
- [S7] Generative AI Policy

</details>

---

## Follow-up (uses conversation history)

**Request:** Which of those relate to procurement?

**Routed to:** `answer_question` (Follow-up asks which items from the GCS image-generation answer relate to procurement, which needs a document lookup.) · routed by model · 8.5s

**Image-generation uses:** None of the permitted uses in the excerpt relate to procurement. They are:
- Varying campaign imagery for different platforms and formats.
- Producing region-specific visual content.
- Creating infographics for complex statistics [S1].

The excerpt cuts off mid-sentence in this list, so I can't say whether further image uses follow.

**Safeguards that touch procurement:** These are general to the policy, not specific to image generation.
- The policy requires all contracted and framework suppliers to adhere to it and to have safeguards in place [S1].
- Those suppliers "remain responsible for their use of the technology" [S1].
- It commits to engaging with strategic suppliers and technology providers on significant developments in generative AI [S1].

**Not covered:** The excerpts don't mention buying or approving AI tools, vendor selection criteria, or specific contract terms in the GCS policy. The other safeguards I can see are not procurement-related. They cover human-in-the-loop review, factuality, training, and guidance such as ICO, ATRS and ISBA [S1][S8].

The AI Opportunities Action Plan does discuss procurement, including contract standards and "contemplation" clauses [S2]. It is a separate document, so those points shouldn't be attributed to the GCS policy.

<details><summary>Sources</summary>

- [S1] Generative AI Policy
- [S2] AI Opportunities Action Plan
- [S8] Generative AI Policy

</details>

---

## Multi-intent request

**Request:** Give me a short summary and the top 5 opportunities

**Routed to:** `executive_summary` (User wants a short summary of the documents.); `extract_insights` (User wants the top 5 opportunities across the documents.) · routed by model · 41.0s

# Executive summary

**Bottom line:** The UK is backing AI strongly, but concentrated compute and data, integrated firms and false outputs need active management, and Government plans lack costings.

## Key messages
- The CMA finds foundation model competition currently vibrant, but warns of risks from data access, compute costs, vertical integration and lock-in.
- A few large firms hold compute and data. GPT-4 training reportedly cost over $100 million, and high-quality public data could run out within about three years.
- The Action Plan (13 January 2025) makes 50 recommendations, including a 20x expansion of the AI Research Resource by 2030.
- Government guidance, including the AI Playbook's 10 principles, sets expectations for safe, secure use.

## Main risks
- **Barriers to entry:** CSP partners get priority compute, and none of the three biggest cloud providers offers NVIDIA A100s in the UK.
- **Consumer harm:** Hallucinations are unlikely to be eliminated. Fake reviews, phishing and unlabelled advertising may breach consumer law, and responsibility across supply chains is unclear.
- **Delivery:** The Action Plan relies on long-term funding without costed detail, and flags regulatory lag, IP uncertainty and skills shortages.

## Opportunities
- Scan, Pilot, Scale and a UK Sovereign AI unit could build homegrown capability.
- The Foundation Model Taskforce has £100 million start-up funding, plus around £900 million for compute.
- The DMCC Bill will expand CMA powers, and open-source models could widen competition.

## Recommended next steps
- Review the full Action Plan, Government response and 118-page AI Playbook. These were unavailable here, so owners and timelines remain unverified.
- Seek a costed delivery plan, starting with the six-month infrastructure plan.
- Back the CMA's principles on disclosure, redress, data portability and interoperability, and consult the Government AI Security Team on secure deployment.

*278 words · based on 11 documents*

---

### Opportunities

| # | Item | Detail | Owner | Date | Priority | Source |
|---|---|---|---|---|---|---|
| 1 | **Large economic upside from AI adoption** | AI adoption could add £400 billion to the UK economy by 2030, and broad uptake of foundation models could triple productivity growth. Global GDP is predicted to rise 7 percent over a decade. | UK government; UK citizens; UK economy | By 2030; Over a decade (global GDP projection) | High | AI Opportunities Action Plan; AI Opportunities Action Plan Publication; Foundation Model Taskforce |
| 2 | **Open-source and fine-tuned models lower entry barriers and discipline incumbents** | Fine-tuning needs far less compute, and open models such as Alpaca ($600) and Vicuna-13B (around 90% of ChatGPT quality) approach closed-model performance. This could constrain closed-source providers where cutting-edge performance is unnecessary. | Open-source developers; Academic and open research organisations; new entrants; FM developers | - | High | AI Foundation Models Initial Report, p.42; AI Foundation Models Short Report, p.15; AI Foundation Models Initial Report, p.37; AI Foundation Models Initial Report, p.45 |
| 3 | **Competition and regulation can drive quality and reliability** | Outcomes improve if developers face competitive pressure on reliability and accuracy, supported by standardised benchmarks. Once the DMCC Bill is in force, the CMA can set targeted conduct requirements on firms with strategic market status. | FM developers and deployers; Competition and Markets Authority | - | High | AI Foundation Models Initial Report, p.102; AI Foundation Models Short Report, p.36 |
| 4 | **Foundation models can empower smaller players and downstream firms** | Foundation models can boost productivity across firms of many sizes and help smaller search engines and start-ups compete with incumbents. Easy switching and multi-homing among deployment options is a key competitive driver. | Start-ups and smaller firms; Small and medium businesses; Smaller search engines; Downstream firms | - | Medium | AI Foundation Models Initial Report, p.55; AI Foundation Models Initial Report, p.66; AI Foundation Models Short Report, p.25; AI Foundation Models Initial Report, p.57 |
| 5 | **Efficiency and service gains in the public sector** | Examples include DVSA risk scoring cutting enforcement preparation time by 50% and ESO solar forecasts 33% more accurate. Generative AI aids content production, and foundation models could speed healthcare diagnoses and free teachers' time. | Driver and Vehicle Standards Agency; National Grid ESO; Government communicators | - | Medium | Guide to Using AI in Public Sector, p.9; Generative AI Policy; Foundation Model Taskforce |

<details><summary>Sources</summary>

- AI Foundation Models Initial Report
- AI Foundation Models Short Report
- AI Opportunities Action Plan
- AI Opportunities Action Plan Publication
- AI Playbook for UK Government
- AI Safety Institute
- AI Security Guidance
- Foundation Model Taskforce
- GDS AI Index
- Generative AI Policy
- Guide to Using AI in Public Sector
- AI Foundation Models Initial Report, p.102
- AI Foundation Models Initial Report, p.37
- AI Foundation Models Initial Report, p.42
- AI Foundation Models Initial Report, p.45
- AI Foundation Models Initial Report, p.55
- AI Foundation Models Initial Report, p.57
- AI Foundation Models Initial Report, p.66
- AI Foundation Models Short Report, p.15
- AI Foundation Models Short Report, p.25
- AI Foundation Models Short Report, p.36
- Guide to Using AI in Public Sector, p.9

</details>

---

## Out of scope

**Request:** What's the weather in London?

**Routed to:** `respond_directly` (Weather is unrelated to the loaded AI policy documents, so I'm declining and explaining what I can do.) · routed by model · 2.3s

I can't help with the weather in London. I only work with the loaded UK government publications on AI policy, safety, security and adoption. I can answer specific questions about them, summarise them, list risks, opportunities, actions, deadlines or stakeholders, or show which documents are loaded. Would you like any of those?

---

## Data-quality awareness

**Request:** Which documents are loaded, and are there any problems with them?

**Routed to:** `list_documents` (User asks which documents are loaded and any data-quality problems.) · routed by model · 1.6s

11 documents loaded (~83,856 words).

| Document | Type | Pages | Words | Notes |
|---|---|---|---|---|
| AI Foundation Models Initial Report | PDF | 129 | 49,141 | - |
| AI Foundation Models Short Report | PDF | 38 | 12,602 | - |
| AI Opportunities Action Plan | HTML | web page | 8,642 | - |
| AI Opportunities Action Plan Publication | HTML | web page | 251 | Short page (~251 words after cleaning): likely a landing or index page, not the full document. |
| AI Playbook for UK Government | HTML | web page | 290 | File has a .pdf extension but is actually HTML; parsed as html. Short page (~290 words after cleaning): likely a landing or index page, not the full document. |
| AI Safety Institute | HTML | web page | 213 | Short page (~213 words after cleaning): likely a landing or index page, not the full document. |
| AI Security Guidance | HTML | web page | 357 | Short page (~357 words after cleaning): likely a landing or index page, not the full document. |
| Foundation Model Taskforce | HTML | web page | 1,206 | - |
| GDS AI Index | HTML | web page | 279 | Short page (~279 words after cleaning): likely a landing or index page, not the full document. |
| Generative AI Policy | HTML | web page | 1,873 | - |
| Guide to Using AI in Public Sector | PDF | 48 | 9,002 | - |

---
